import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as lines 
from typing import Optional
import numpy as np

import warnings
from collections.abc import Iterable, Collection
from numbers import Number
from dataclasses import dataclass, field


@dataclass
class Box():
    xy: tuple[int]
    width: int
    height: int
    params: dict = field(default_factory=dict)
    
    def to_dict(self):
        box_dict = self.__dict__.copy()
        box_dict.update(box_dict.pop('params'))
        return box_dict
    
    
class Chromosome():
    def __init__(self, length, name='chr', 
                 centromere=None, locuses=None):
        self.name = name
        self.length = length
        self.centromere = centromere
        self.locuses = locuses
        
    def __len__(self):
        return self.length
    
    def _check_coord(self, coord, coord_type='coordinate'):
        if not isinstance(coord, Number):
            raise ValueError(f'The {coord_type} should be a number!')
        if not (0 <= coord <= self.length):
            raise KeyError(f'Your {coord_type} {coord} is' + \
                           f' out of {self.name} length!' +\
                           f' The len is {self.length} bp.'
                          )
    
    def __getitem__(self, coord):
        self._check_coord(coord)
        return coord / self.length
    
    @property
    def centromere(self):
        return self._centromere

    @property
    def locuses(self):
        locuses = self._locuses
        if isinstance(locuses, Iterable):
            locuses = [locus / self.length for locus in locuses]
        return locuses
    
    @centromere.setter
    def centromere(self, centromere):
        if centromere is not None:
            self._check_coord(centromere)
        self._centromere = centromere
    
    @locuses.setter
    def locuses(self, locuses):
        if not locuses is None:      
            if not isinstance(locuses, Iterable):
                locuses = [locuses]
            for locus in locuses:
                self._check_coord(locus, coord_type='locus')
        self._locuses = locuses
    
    @staticmethod
    def _add_box_to_ax(ax, box: dict):
        rect = patches.FancyBboxPatch(**box)
        ax.add_patch(rect)
        return rect
    
    def _plot_locuses(self, ax,
                      x, y, width, height,
                      linewidth, pad, locuses_color,
                      show_centromere, show_extentions,
                      locuses_lines_props, x_grid
                     ):
        
        line_props = {
            'lw': linewidth,
            'color': locuses_color,
            'solid_joinstyle': 'round'
        }
        if locuses_lines_props is not None:
            line_props.update(locuses_lines_props)
            
        if x_grid is None:
            x_grid = np.linspace(x, width, len(self.locuses)+2)[1:-1]
        elif len(x_grid) != len(self.locuses):
            raise ValueError(f'X grid len ({len(x_grid)}) should' +\
                             f'be equal number of locuses ({len(x_grid)})!')
        for locus, grid_point in zip(self.locuses, x_grid):
            locus = locus * width
            extend = 0.06 * height
            lower = y-extend
            upper = y+height+extend
            xs = [locus, locus]
            ys = [upper, lower]
            
            if show_extentions:
                v_length = (upper - lower) / 2
                xs.extend([grid_point, grid_point])
                ys.extend([lower - v_length,  lower - 2 * v_length])
                
                ax.set_ylim(y-pad-2 * v_length, height + pad)
                
            line = lines.Line2D(xs, ys, **line_props) 
            ax.add_line(line)    
                

        
    
    def plot_chromosome(self, *,
                        ax = None,
                        x = 0,
                        y = 0,
                        width = 100,
                        height = 5,
                        corner_radius = 2.5,
                        linewidth = 2,
                        edgecolor = 'black',
                        facecolor = '#e4f2f9',
                        gap = .6,
                        pad = 1.5,
                        locuses_color='red',
                        show_centromere = True,
                        show_axes = False,
                        show_name = True,
                        show_locuses = True,
                        show_extentions = True,
                        locuses_lines_props = None,
                        locuses_x_grid = None
                       ):
        
        
        if ax is None:
            ax = plt.gca()
        ax.set_xlim(x-pad, width + pad)
        ax.set_ylim(y-pad, height + pad)
        ax.set_aspect('equal', 'box')

        box_params = {
            'linewidth': linewidth,
            'edgecolor': edgecolor,
            'facecolor': facecolor,
            'boxstyle': f'round, rounding_size={corner_radius}'
        }      
        

        if show_centromere:
            if self.centromere is None:
                raise ValueError('Please set or pass centromere coordinate!')
                
            centromere = self.centromere * width / self.length
            box1 = Box((x, y), 
                       centromere - gap, 
                       height, 
                       box_params)
            box2 = Box((centromere, y), 
                       width - centromere + gap, 
                       height, 
                       box_params)
            self._add_box_to_ax(ax, box1.to_dict())
            self._add_box_to_ax(ax, box2.to_dict())   
        else:
            box = Box((x, y), width, height, box_params)
            self._add_box_to_ax(ax, box.to_dict())
            
        if show_locuses:
            locuses = self.locuses
            if locuses is None:
                msg = 'It seems like you have '+\
                      'empty locuses. Check the "locuses" '+\
                      'attribute of the chromosome. '+\
                      'No locuses to be plotted.'
                warnings.warn(msg)
            else:
                self._plot_locuses(ax, x = x, y = y, x_grid = locuses_x_grid,
                                   width = width, height = height,
                                   linewidth = linewidth, pad = pad,
                                   locuses_color = locuses_color,
                                   show_centromere = show_centromere,
                                   show_extentions = show_extentions,
                                   locuses_lines_props = locuses_lines_props
                )

        if not show_axes:
            ax.set_axis_off()
            
        if show_name:
            ax.set_title(f'Chromosome {self.name}')     

    @staticmethod
    def parse_chromsizes():
        pass
        
