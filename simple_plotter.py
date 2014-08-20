#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import matplotlib

from cnl_library import CNLParser, calc_ema, merge_lists, pretty_json

## matplotlib.use('QT4Agg')  # override matplotlibrc
import matplotlib.pyplot as plt


def append_twice(base_list, extend_list):
    if ( isinstance(extend_list, list) ):
        for x in extend_list:
            base_list.append(x)
            base_list.append(x)
    else:
        base_list.append(extend_list)
        base_list.append(extend_list)





def parse_cnl_file(filename):
    ## * Parse input file. *
    cnl_file = CNLParser(filename)

    ## Prepare data for matplotlib

    #nics = cnl_file.get_nics()
    nics = ("eth1", "eth2")  ## XXX
    net_cols = list()
    nic_fields = [".send", ".receive"]
    for nic_name in nics:
        for nic_field in nic_fields:
            net_cols.append( nic_name + nic_field )

    cpu_cols = [ cpu_name + ".util" for cpu_name in cnl_file.get_cpus() ]

    cols = cnl_file.get_csv_columns()
    #x_values = cols["end"]
    #print( cols )   ## XXX


    ## Augment cnl_file with processed data.
    cnl_file.cols = cols
    cnl_file.net_col_names = net_cols
    cnl_file.cpu_col_names = cpu_cols
    #cnl_file.x_values = x_values

    return cnl_file




def plot(ax, x_values, cols, active_cols, **kwargs):
    #use_ema = kwargs.get("use_ema")

    for col_name in active_cols:
        data = cols[col_name]
        if ( len(x_values) == len(data)*2 ):
            data = merge_lists( data, data )

        # * plot *
        ax.plot(x_values , data, label=col_name)

        ## plot ema
        #if ( use_ema ):
            #ax.plot(x_values , calc_ema(cols[col_name], 0.2), label=col_name+" (ema)")


def plot_net(ax, cnl_file):
    ax.set_ylim(0,10**10)
    ax.set_ylabel('Throughput (Bit/s)')

    plot(ax, cnl_file.x_values, cnl_file.cols, cnl_file.net_col_names)

    ax.legend(loc=0)
    #ax.legend(loc=8)


def plot_cpu(ax, cnl_file):
    ax.set_ylim(0,100)
    ax.set_ylabel('CPU util (%)')

    plot(ax, cnl_file.x_values, cnl_file.cols, cnl_file.cpu_col_names)

    ax.legend(loc=0)
    #ax.legend(loc=1)




## MAIN ##
if __name__ == "__main__":

    num_files = len(sys.argv) - 1

    ## Create figure (window/file)
    fig = plt.figure()
    fig.canvas.set_window_title('CPUnetPlot')

    old_ax_net = None
    old_ax_cpu = None
    for i in range(1, num_files+1):
        ## Read file
        filename = sys.argv[i]
        cnl_file = parse_cnl_file(filename)

        print( filename )
        print( pretty_json(cnl_file.get_general_header()) )
        print()

        ## Plot with matplotlib.

        ## Draw comment on the figure (use absolute positioning).
        t = matplotlib.text.Text(10,10, "Comment: " + cnl_file.get_comment(), figure=fig)
        fig.texts.append(t)


        ## Prepare subplots
        ax_net = fig.add_subplot(2, num_files, i, sharex=old_ax_net, sharey=old_ax_net)
        ax_cpu = fig.add_subplot(2, num_files, i+num_files, sharex=ax_net, sharey=old_ax_cpu)
        #ax_net = fig.add_subplot(111)  ## twin axis
        #ax_cpu = ax_net.twinx()        ## twin axis


        ## Prepare x_values
        plateau = True      ## XXX
        if ( plateau ):
            cnl_file.x_values = merge_lists( cnl_file.cols["begin"], cnl_file.cols["end"] )
        else:
            cnl_file.x_values = cnl_file.cols["end"]

        ## Plot
        plot_net(ax_net, cnl_file)
        plot_cpu(ax_cpu, cnl_file)

        old_ax_net = ax_net
        old_ax_cpu = ax_cpu


    ## maximize window
    if ( num_files > 1 ):
        try:
            figManager = plt.get_current_fig_manager()
            figManager.window.showMaximized()
        except:
            pass

    # show plot
    plt.show()
