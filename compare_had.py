#!/usr/bin/env python
"""
Takes multiple HDF files and compares them in a plot
 
Created on Mon Aug 22 16:25:09 2016

@author: lelekew

"""

import os
from Tkinter import *
import tkMessageBox
from plot_had import PlotHaD as hplt
import time as TIME
from pyhdf import RasHDF as rHDF

def compare_hdf_files(hdf_filenames, working_directory, plot_directory, data_directory, coords_txt_file, r1D_comp_filename, obs_paths_filename, obs_dss, dss_2D_filename):
    hdf_objects = []
    for filename in hdf_filenames:
        hdf = rHDF(filename, working_directory)
        hdf.get_data(data_directory, coords_txt_file, r1D_comp_filename, obs_paths_filename, obs_dss, dss_2D_filename)
        hdf_objects.append(hdf)
    
    cHAD = CompareHaD(plot_directory, hdf_objects)
    cHAD.store_plot_stacks()
    
def compare_hdf_files_segment(hdf_filenames, working_directory, plot_directory, data_directory, coords_txt_file, r1D_comp_filename, obs_paths_filename, obs_dss, dss_2D_filename, bounds):
    hdf_objects = []
    for filename in hdf_filenames:
        hdf = rHDF(filename, working_directory)
        hdf.get_data(data_directory, coords_txt_file, r1D_comp_filename, obs_paths_filename, obs_dss, dss_2D_filename)
        hdf_objects.append(hdf)
    
    cHAD = CompareHaD(plot_directory, hdf_objects)
    cHAD.store_plot_stacks_segment(bounds)
    
class CompareHaD(object):
    def __init__(self, plot_directory, hdf_objects):
        self.plot_directory = plot_directory
        self.hdf_objects = hdf_objects
        clear = True
        name_string = ''
        self.units = hdf_objects[0].units
        for hdf in hdf_objects:
            if hdf.has_data == False:
                clear = False
            if name_string.split() == []:
                name_string = hdf.shortID
            else:
                name_string = name_string + ' & ' + hdf.shortID
        if clear == False:
            message = "One or more of your hdf files do not have data."
            self.error_box(message)
        self.name_string = name_string
        plot_subfolder = self.plot_directory + '\\' + self.name_string
        self.plot_subfolder = plot_subfolder.replace(" ","_")
        self.num_hdf = len(self.hdf_objects)
        self.flow_keys = []
        self.stage_keys = []
        self.base_time=TIME.clock()
        self.assemble_data()
        
    def error_box(self,message_text):
        window = Tk()
        window.wm_withdraw()
        window.geometry("1x1+"+str(window.winfo_screenwidth()/2)+"+"+str(window.winfo_screenheight()/2))
        tkMessageBox.showinfo(title="Error", message=message_text)
        window.lift()
        window.mainloop()
            
    def assemble_data(self):
        # Uses first hdf file to determine gages to compute:
        self.flow_keys = self.hdf_objects[0].ras_computed_flow.keys()
        self.stage_keys = self.hdf_objects[0].ras_computed_stage.keys()
        self.flow_time_dict = {}
        self.flow_data_dict = {}
        self.flow_color_dict = {}
        self.flow_series_names_dict = {}
        for key in self.flow_keys:
            time_lists = []
            data_lists = []
            series_name = []
            colors = []
            if key in self.hdf_objects[0].obs_flow:
                time_lists.append(self.hdf_objects[0].time_minutes_flow_obs[key])
                data_lists.append(self.hdf_objects[0].obs_flow[key])
                series_name.append("Observed")
                colors.append('k')
            time_lists.append(self.hdf_objects[0].time_minutes_flow_comp[key])
            data_lists.append(self.hdf_objects[0].ras_computed_flow[key])
            series_name.append(self.hdf_objects[0].shortID + " Computed")
            comp_colors = ['b','g','r','y'] #change plot computed line color here
            colors.append(comp_colors[0])
            
            if self.num_hdf > 1:
                for i in range(self.num_hdf)[1:]:
                    colors.append(comp_colors[i])
                    #loop through and find all complimentary flow data
                    if key in self.hdf_objects[i].ras_computed_flow:
                        time_lists.append(self.hdf_objects[i].time_minutes_flow_comp[key])
                        data_lists.append(self.hdf_objects[i].ras_computed_flow[key])
                        series_name.append(self.hdf_objects[i].shortID + " Computed")
            self.flow_time_dict[key], self.flow_data_dict[key], self.flow_color_dict[key], self.flow_series_names_dict[key] = time_lists, data_lists, colors, series_name
       
        self.stage_time_dict = {}
        self.stage_data_dict = {}
        self.stage_color_dict = {}
        self.stage_series_name_dict = {}
        for key in self.stage_keys:
            time_lists = []
            data_lists = []
            series_name = []
            if key in self.hdf_objects[0].obs_stage:
                time_lists.append(self.hdf_objects[0].time_minutes_stage_obs[key])
                data_lists.append(self.hdf_objects[0].obs_stage[key])
                series_name.append("Observed")
            time_lists.append(self.hdf_objects[0].time_minutes_stage_comp[key])
            data_lists.append(self.hdf_objects[0].ras_computed_stage[key])
            series_name.append(self.hdf_objects[0].shortID + " Computed")
            comp_colors = ['b','g','r','y'] #change plot computed line color here
            colors.append(comp_colors[0])
            
            if self.num_hdf > 1:
                for i in range(self.num_hdf)[1:]:
                    colors.append(comp_colors[i])
                    #loop through and find all complimentary stage data
                    if key in self.hdf_objects[i].ras_computed_stage:
                        time_lists.append(self.hdf_objects[i].time_minutes_stage_comp[key])
                        data_lists.append(self.hdf_objects[i].ras_computed_stage[key])
                        series_name.append(self.hdf_objects[i].shortID + " Computed")
            self.stage_time_dict[key], self.stage_data_dict[key], self.stage_color_dict[key], self.stage_series_name_dict[key] = time_lists, data_lists, colors, series_name 
    
    # Go through all gages and plot them and save them in a folder under the plot_subfolder
    def store_plot_stacks(self):
        font_size = 20
        
        if not os.path.exists(self.plot_subfolder): 
            os.makedirs(self.plot_subfolder)
            
        line_widths = [2 for x in range(self.num_hdf+1)] #for now all possible plots are of width 2
        line_styles = ['-' for x in range(self.num_hdf+1)]
        
        for key in self.flow_data_dict:
            current_time = TIME.clock()-self.base_time
            print 'Plotting and saving %s gage flow comparison... %s seconds' %(key,current_time)
            time_lists = self.flow_time_dict[key]
            data_lists = self.flow_data_dict[key]
            series_names = self.stage_series_name_dict[key]
            line_colors = self.stage_color_dict[key]
            self.had_plot = hplt(self.plot_subfolder, "flow_stack", key, time_lists, data_lists, series_names, self.units)
            self.had_plot.plot_save_stack(line_colors, line_styles, line_widths, font_size)
        for key in self.stage_data_dict:
            current_time = TIME.clock()-self.base_time
            print 'Plotting and saving %s gage stage comparison... %s seconds' %(key,current_time)
            time_lists = self.stage_time_dict[key]
            data_lists = self.stage_data_dict[key]
            series_names = self.stage_series_name_dict[key]
            line_colors = self.stage_color_dict[key]
            self.had_plot = hplt(self.plot_subfolder, "stage_stack", key, time_lists, data_lists, series_names, self.units)
            self.had_plot.plot_save_stack(line_colors, line_styles, line_widths, font_size)
    
    # Go through all gages and plot them and save them in a folder under the plot_subfolder
    def store_plot_stacks_segment(self, bounds):
        font_size = 20
        
        if not os.path.exists(self.plot_subfolder): 
            os.makedirs(self.plot_subfolder)
            
        line_widths = [2 for x in range(self.num_hdf+1)] #for now all possible plots are of width 2
        line_styles = ['-' for x in range(self.num_hdf+1)]                   
                       
        for key in self.flow_data_dict:
            current_time = TIME.clock()-self.base_time
            print 'Plotting and saving %s gage flow comparison... %s seconds' %(key,current_time)
            time_lists = self.flow_time_dict[key]
            data_lists = self.flow_data_dict[key] 
            series_names = self.stage_series_name_dict[key]
            line_colors = self.stage_color_dict[key]
            self.had_plot = hplt(self.plot_subfolder, "flow_stack", key, time_lists, data_lists, series_names, self.units)
            self.had_plot.plot_save_stack_segment(line_colors, line_styles, line_widths, font_size, bounds)
        for key in self.stage_data_dict:
            current_time = TIME.clock()-self.base_time
            print 'Plotting and saving %s gage stage comparison... %s seconds' %(key,current_time)
            time_lists = self.stage_time_dict[key]
            data_lists = self.stage_data_dict[key]
            series_names = self.stage_series_name_dict[key]
            line_colors = self.stage_color_dict[key]
            self.had_plot = hplt(self.plot_subfolder, "stage_stack", key, time_lists, data_lists, series_names, self.units)
            self.had_plot.plot_save_stack_segment(line_colors, line_styles, line_widths, font_size, bounds)