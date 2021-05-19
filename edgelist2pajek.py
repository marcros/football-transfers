# CREDITS TO: https://gist.github.com/conradlee/1331132

import os
import sys
import subprocess
import optparse
import tempfile


# Special feature: can convert files so large that they
# don't fit in memory. Works for weighted/unweighted,
# directed/undirected edges.

def edgelist_to_pajek(input_filename, output_filename="", directed=False, weighted=False, buffer_size=500):
    """
    Input filename is the name of an edgelist file with the following format
       node1ID node2ID [weight]
       node1ID node3ID [weight]
       ...
       nodeiID nodejID [weight]
    where nodeIDs are separated by whitespace.

    Edge weights will only be used if the "weighted" argument is set to True.

    Buffer size is in megabytes.

    If output is unspecified, then I use stdout.
    """
    # Sort out I/O
    if output_filename:
        output_file = open(output_filename, "w")
    else:
        output_file = sys.stdout

    node_idx_map = {}
    # Write vertices section and produce map from original nodeIDs to
    # contiguous integer ids that start from one.
    with Tempfile() as unique_nodes_file:
        unique_nodes_command = "<%s awk '{ print $1; print $2; }' | sort -n --buffer-size=%dM | uniq>%s" % (
        input_filename, buffer_size, unique_nodes_file.name)
        unique_nodes_command = "<" + input_filename + " " + unique_nodes_command
        run_command(unique_nodes_command)
        num_nodes = int(run_command("wc -l %s" % unique_nodes_file.name).split()[0])
        output_file.write("*Vertices\t%d\n" % num_nodes)
        with open(unique_nodes_file.name) as nodes_file:
            for idx, line in enumerate(nodes_file):
                node_id = int(line.rstrip("\n"))
                pajek_idx = idx + 1  # Pajek indexing starts with 1
                output_file.write('\t%d "%d"\n' % (pajek_idx, node_id))
                # Might be slow to add to dict this way, one at a time
                node_idx_map[node_id] = pajek_idx

    # Now write edges
    if directed:
        output_file.write("*Arcs\n")
    else:
        output_file.write("*Edges\n")

    input_file = open(input_filename)
    for i, line in enumerate(input_file):
        try:
            if weighted:

                n1, n2, weight = line.strip().split()
                output_file.write("\t%d\t%d\t%0.6f\n" % (node_idx_map[int(n1)],
                                                         node_idx_map[int(n2)],
                                                         float(weight)))
            else:
                n1, n2 = map(int, line.strip().split()[:2])
                output_file.write("\t%d\t%d\n" % (node_idx_map[n1],
                                                  node_idx_map[n2]))
        except ValueError:
            raise ValueError("Problem parsing input file on line %d, which reads: \n\t%s\nIf you selected the -w option for weighted edegs, make sure this line has an edg\
e weight" % (i + 1, line))
    input_file.close()
    output_file.close()


def run_command(command):
    # Necessary for compatability with python 2.6 which is missing
    # some of the conveneince funcitons in python 2.7
    """ Warning: Will hang if stderr or stdout is large """
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    retcode = process.wait()
    if retcode != 0:
        raise Exception("Problem running command: " + command)
    stdout, stderr = process.communicate()
    return stdout


class Tempfile:
    def __enter__(self):
        self.file = tempfile.NamedTemporaryFile(delete=False)
        return self.file

    def __exit__(self, type, value, traceback):
        try:
            os.remove(self.file.name)
        except OSError:
            pass


if __name__ == "__main__":
    parser = optparse.OptionParser(usage="Usage: %prog input_filename <options>")
    parser.add_option('-d',
                      help="specifies that edges are directed.",
                      dest="directed",
                      default=False,
                      action="store_true")
    parser.add_option('-w',
                      help="specifies that edges are weighted.",
                      dest="weighted",
                      default=False,
                      action="store_true")
    parser.add_option('-o',
                      "--out_filename",
                      help="Filename for output, which is in pajek format. Default [stdout]",
                      dest="out_filename",
                      type="string",
                      default="")
    parser.add_option('-b',
                      "--buffer_size",
                      help="Size of buffer for sort command to use (in megabytes) Default [%default]",
                      dest="buffer_size",
                      type="int",
                      default=500)

    (opts, args) = parser.parse_args()
    input_filename = sys.argv[1]
    edgelist_to_pajek(input_filename,
                      output_filename=opts.out_filename,
                      directed=opts.directed,
                      weighted=opts.weighted,
                      buffer_size=opts.buffer_size)