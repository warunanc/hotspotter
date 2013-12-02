''' Lots of functions for drawing and plotting visiony things '''
from __future__ import division, print_function
import __builtin__
import sys
import matplotlib
from _localhelpers.draw_func2_helpers import *
from matplotlib import gridspec
from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.patches import Rectangle, Circle, FancyArrow
from matplotlib.transforms import Affine2D
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
import pylab
import sys
import types
import warnings
import itertools
from itertools import izip
import helpers
import re
import params
import os
#print('LOAD_MODULE: draw_func2.py')

# Toggleable printing
print = __builtin__.print
print_ = sys.stdout.write
def print_on():
    global print, print_
    print =  __builtin__.print
    print_ = sys.stdout.write
def print_off():
    global print, print_
    def print(*args, **kwargs): pass
    def print_(*args, **kwargs): pass
# Dynamic module reloading
def reload_module():
    import imp, sys
    print('[df2] reloading '+__name__)
    imp.reload(sys.modules[__name__])
    helpermodule = sys.modules['_localhelpers.draw_func2_helpers']
    print('[df2] reloading '+__name__)
    imp.reload(sys.modules[__name__])
def rrr(): reload_module()

DISTINCT_COLORS = True #and False
DARKEN = None
ELL_LINEWIDTH = 1.5
if DISTINCT_COLORS: 
    ELL_ALPHA  = .6
    LINE_ALPHA = .35
else:
    ELL_ALPHA  = .4
    LINE_ALPHA = .4
ELL_COLOR  = BLUE

LINE_COLOR = RED
LINE_WIDTH = 1.4

SHOW_LINES = True #True
SHOW_ELLS  = True

POINT_SIZE = 2

def my_prefs():
    global LINE_COLOR
    global ELL_COLOR
    global ELL_LINEWIDTH
    global ELL_ALPHA
    LINE_COLOR = (1, 0, 0)
    ELL_COLOR = (0, 0, 1)
    ELL_LINEWIDTH = 2
    ELL_ALPHA = .5


def execstr_global():
    execstr = ['global' +key for key in globals().keys()]
    return execstr

# ---- IMAGE CREATION FUNCTIONS ---- 
def draw_sift(desc, kp=None):
    '''
    desc = np.random.rand(128)
    desc = desc / np.sqrt((desc**2).sum())
    desc = np.round(desc * 255)
    '''
    ax = plt.gca()
    tau = np.float64(np.pi * 2)
    DSCALE = .25
    XYSCALE = .5
    XYSHIFT = -.75
    THETA_SHIFT = 1/8 * tau
    # SIFT CONSTANTS
    NORIENTS = 8; NX = 4; NY = 4; NBINS = NX * NY
    def cirlce_rad2xy(radians, mag):
        return np.cos(radians)*mag, np.sin(radians)*mag
    discrete_theta = (np.arange(0,NORIENTS)*(tau/NORIENTS) + THETA_SHIFT)[::-1]
    # Build list of plot positions
    dim_mag   = desc / 255.0
    dim_theta = np.tile(discrete_theta, (NBINS, 1)).flatten()
    dim_xy = np.array(zip(*cirlce_rad2xy(dim_theta, dim_mag))) 
    yxt_gen = itertools.product(xrange(NY),xrange(NX),xrange(NORIENTS))
    yx_gen  = itertools.product(xrange(NY),xrange(NX))

    # Transforms
    axTrans = ax.transData
    kpTrans = None
    if kp is None:
        kp = [0, 0, 1, 0, 1]
    kp = np.array(kp)   
    kpT = kp.T
    x, y, a, c, d = kpT[:,0]
    #a_ = 1/a
    #b_ = (-c)/(a*d)
    #d_ = 1/d
    #a_ = 1/np.sqrt(a) 
    #b_ = c/(-np.sqrt(a)*d - a*np.sqrt(d))
    #d_ = 1/np.sqrt(d)
    transMat = [( a, 0, x),
                ( c, d, y),
                ( 0, 0, 1)]
    kpTrans = Affine2D(transMat)
    axTrans = ax.transData
    #print('\ntranform=%r ' % transform)
    # Draw Arms
    arrow_patches = []
    arrow_patches2 = []
    for y,x,t in yxt_gen:
        #print((x, y, t))
        #index = 127 - ((NY - 1 - y)*(NX*NORIENTS) + (NX - 1 - x)*(NORIENTS) + (NORIENTS - 1 - t))
        index = ((y)*(NX*NORIENTS) + (x)*(NORIENTS) + (t))
        #index = ((NY - 1 - y)*(NX*NORIENTS) + (NX - 1 - x)*(NORIENTS) + (t))
        #print(index)
        (dx, dy) = dim_xy[index]
        arw_x  = ( x*XYSCALE) + XYSHIFT
        arw_y  = ( y*XYSCALE) + XYSHIFT
        arw_dy = (dy*DSCALE) * 1.5 # scale for viz Hack
        arw_dx = (dx*DSCALE) * 1.5
        posA = (arw_x, arw_y)
        posB = (arw_x+arw_dx, arw_y+arw_dy)
        arw_patch = FancyArrow(arw_x, arw_y, arw_dx, arw_dy, head_width=.0001,
                               transform=kpTrans, length_includes_head=False)
        arw_patch2 = FancyArrow(arw_x, arw_y, arw_dx, arw_dy, head_width=.0001,
                                transform=kpTrans, length_includes_head=False)
        arrow_patches.append(arw_patch)
        arrow_patches2.append(arw_patch2)
    # Draw Circles
    circle_patches = []
    for y,x in yx_gen:
        circ_xy = ((x*XYSCALE)+XYSHIFT, (y*XYSCALE)+XYSHIFT)
        circ_radius = DSCALE
        circ_patch = Circle(circ_xy, circ_radius,
                               transform=kpTrans)
        circle_patches.append(circ_patch)
        
    circ_collection = matplotlib.collections.PatchCollection(circle_patches)
    circ_collection.set_facecolor('none')
    circ_collection.set_transform(axTrans)
    circ_collection.set_edgecolor(BLACK)
    circ_collection.set_alpha(.5)

    # Body of arrows
    arw_collection = matplotlib.collections.PatchCollection(arrow_patches)
    arw_collection.set_transform(axTrans)
    arw_collection.set_linewidth(.5)
    arw_collection.set_color(RED)
    arw_collection.set_alpha(1)

    #Border of arrows
    arw_collection2 = matplotlib.collections.PatchCollection(arrow_patches2)
    arw_collection2.set_transform(axTrans)
    arw_collection2.set_linewidth(1)
    arw_collection2.set_color(BLACK)
    arw_collection2.set_alpha(1)

    ax.add_collection(circ_collection)
    ax.add_collection(arw_collection2)
    ax.add_collection(arw_collection)

def feat_scores_to_color(fs, cmap_='hot'):
    assert len(fs.shape) == 1, 'score must be 1d'
    cmap = plt.get_cmap(cmap_)
    mins = fs.min()
    rnge = fs.max() - mins
    if rnge == 0:
        return [cmap(.5) for fx in xrange(len(fs))]
    score2_01 = lambda score: .1+.9*(float(score)-mins)/(rnge)
    colors    = [cmap(score2_01(fs[fx])) for fx in xrange(len(fs))]
    return colors

def draw_matches2(kpts1, kpts2, fm=None, fs=None, kpts2_offset=(0,0),
                  color_list=None):
    if not DISTINCT_COLORS:
        color_list = None
    # input data
    if not SHOW_LINES:
        return 
    if fm is None: # assume kpts are in director correspondence
        assert kpts1.shape == kpts2.shape
    if len(fm) == 0: 
        return
    ax = plt.gca()
    woff, hoff = kpts2_offset
    # Draw line collection
    kpts1_m = kpts1[fm[:,0]].T
    kpts2_m = kpts2[fm[:,1]].T
    xxyy_iter = iter(zip(kpts1_m[0],
                         kpts2_m[0]+woff,
                         kpts1_m[1],
                         kpts2_m[1]+hoff))
    if color_list is None:
        if fs is None: # Draw with solid color
            color_list    = [ LINE_COLOR for fx in xrange(len(fm)) ] 
        else: # Draw with colors proportional to score difference
            color_list = feat_scores_to_color(fs)
    segments  = [((x1, y1), (x2,y2)) for (x1,x2,y1,y2) in xxyy_iter] 
    linewidth = [LINE_WIDTH for fx in xrange(len(fm)) ] 
    line_group = LineCollection(segments, linewidth, color_list, alpha=LINE_ALPHA)
    ax.add_collection(line_group)

def draw_kpts2(kpts, offset=(0,0),
               ell=SHOW_ELLS, 
               pts=False, 
               pts_color=ORANGE, 
               pts_size=POINT_SIZE, 
               ell_alpha=ELL_ALPHA,
               ell_linewidth=ELL_LINEWIDTH,
               ell_color=ELL_COLOR,
               color_list=None,
               wrong_way=False,
               rect=None):
    if not DISTINCT_COLORS:
        color_list = None
    printDBG('drawkpts2: Drawing Keypoints! ell=%r pts=%r' % (ell, pts))
    # get matplotlib info
    ax = plt.gca()
    pltTrans = ax.transData
    ell_actors = []
    eps = 1E-9
    # data
    kpts = np.array(kpts)   
    kptsT = kpts.T
    x = kptsT[0,:] + offset[0]
    y = kptsT[1,:] + offset[1]
    printDBG('[df2] draw_kpts()----------')
    printDBG('[df2] draw_kpts() ell=%r pts=%r' % (ell, pts))
    printDBG('[df2] draw_kpts() drawing kpts.shape=%r' % (kpts.shape,))
    if rect is None:
        rect = ell
        rect = False
        if pts is True:
            rect = False
    if ell or rect:
        printDBG('[df2] draw_kpts() drawing ell kptsT.shape=%r' % (kptsT.shape,))
        a = kptsT[2]
        b = np.zeros(len(a))
        c = kptsT[3]
        d = kptsT[4]
        # Sympy Calculated sqrtm(inv(A) for A in kpts)
        # inv(sqrtm([(a, 0), (c, d)]) = 
        #  [1/sqrt(a), c/(-sqrt(a)*d - a*sqrt(d))]
        #  [        0,                  1/sqrt(d)]
        if wrong_way:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                aIS = 1/np.sqrt(a) 
                bIS = c/(-np.sqrt(a)*d - a*np.sqrt(d))
                dIS = 1/np.sqrt(d)
                cIS = b
                #cIS = (c/np.sqrt(d) - c/np.sqrt(d)) / (a-d+eps)
        else:
            aIS = a
            bIS = b
            cIS = c
            dIS = d
            # Just inverse
            #aIS = 1/a 
            #bIS = -c/(a*d)
            #dIS = 1/d

        kpts_iter = izip(x,y,aIS,bIS,cIS,dIS)
        aff_list = [Affine2D([( a_, b_, x_),
                              ( c_, d_, y_),
                              ( 0 , 0 , 1)])
                    for (x_,y_,a_,b_,c_,d_) in kpts_iter]
        patch_list = []
        ell_actors = [Circle( (0,0), 1, transform=aff) for aff in aff_list]
        if ell:
            patch_list += ell_actors
        if rect:
            rect_actors = [Rectangle( (-1,-1), 2, 2, transform=aff) for aff in aff_list]
            patch_list += rect_actors
        ellipse_collection = matplotlib.collections.PatchCollection(patch_list)
        ellipse_collection.set_facecolor('none')
        ellipse_collection.set_transform(pltTrans)
        ellipse_collection.set_alpha(ell_alpha)
        ellipse_collection.set_linewidth(ell_linewidth)
        if not color_list is None: 
            ell_color = color_list
        ellipse_collection.set_edgecolor(ell_color)
        ax.add_collection(ellipse_collection)
    if pts:
        printDBG('[df2] draw_kpts() drawing pts x.shape=%r y.shape=%r' % (x.shape, y.shape))
        if color_list is None:
            color_list = [pts_color for _ in xrange(len(x))]
        ax.autoscale(enable=False)
        ax.scatter(x, y, c=color_list, s=2*pts_size, marker='o', edgecolor='none')
        #ax.autoscale(enable=False)
        #ax.plot(x, y, linestyle='None', marker='o', markerfacecolor=pts_color, markersize=pts_size, markeredgewidth=0)

# ---- CHIP DISPLAY COMMANDS ----
def imshow(img, 
           fignum=None,
           title=None, 
           figtitle=None, 
           plotnum=None,
           interpolation='nearest', 
           **kwargs):
    #printDBG('[df2] ----- IMSHOW ------ ')
    #printDBG('[df2] *** imshow in fig=%r title=%r *** ' % (fignum, title))
    #printDBG('[df2] *** fignum = %r, plotnum = %r ' % (fignum, plotnum))
    #printDBG('[df2] *** img.shape = %r ' % (img.shape,))
    #printDBG('[df2] *** img.stats = %r ' % (helpers.printable_mystats(img),))
    fig = figure(fignum=fignum, plotnum=plotnum, title=title, figtitle=figtitle, **kwargs)
    ax = plt.gca()
    if not DARKEN is None:
        imgdtype = img.dtype
        img = np.array(img, dtype=float) * DARKEN
        img = np.array(img, dtype=imgdtype) 
    plt.imshow(img, interpolation=interpolation)
    plt.set_cmap('gray')
    ax = fig.gca()
    ax.set_xticks([])
    ax.set_yticks([])
    #ax.set_autoscale(False)
    #try:
        #if plotnum == 111:
            #fig.tight_layout()
    #except Exception as ex:
        #print('[df2] !! Exception durring fig.tight_layout: '+repr(ex))
        #raise
    return fig, ax


def show_matches2(rchip1, rchip2, kpts1, kpts2,
                  fm=None, fs=None, fignum=None, plotnum=None,
                  title=None, vert=None, all_kpts=True, 
                  draw_lines=True,
                  draw_ell=True, 
                  draw_pts=True,
                  ell_alpha=None, **kwargs):
    '''Draws feature matches 
    kpts1 and kpts2 use the (x,y,a,c,d)
    '''
    if fm is None:
        assert kpts1.shape == kpts2.shape
        fm = np.tile(np.arange(0, len(kpts1)), (2,1)).T
    (h1, w1) = rchip1.shape[0:2] # get chip dimensions 
    (h2, w2) = rchip2.shape[0:2]
    woff = 0; hoff = 0 
    if vert is None: # Display match up/down or side/side
        vert = False if h1 > w1 and h2 > w2 else True
    if vert: wB=max(w1,w2); hB=h1+h2; hoff=h1
    else:    hB=max(h1,h2); wB=w1+w2; woff=w1
    # concatentate images
    match_img = np.zeros((hB, wB, 3), np.uint8)
    match_img[0:h1, 0:w1, :] = rchip1
    match_img[hoff:(hoff+h2), woff:(woff+w2), :] = rchip2
    # get matching keypoints + offset
    fig, ax = imshow(match_img, fignum=fignum,
                plotnum=plotnum, title=title,
                **kwargs)
    nMatches = len(fm)
    upperleft_text('#match=%d' % nMatches)
    if all_kpts:
        # Draw all keypoints as simple points
        all_args = dict(ell=False, pts=draw_pts, pts_color=GREEN, pts_size=2, ell_alpha=ell_alpha)
        draw_kpts2(kpts1, **all_args)
        draw_kpts2(kpts2, offset=(woff,hoff), **all_args) 
    if nMatches == 0:
        printDBG('[df2] There are no feature matches to plot!')
    else:
        #color_list = [((x)/nMatches,1-((x)/nMatches),0) for x in xrange(nMatches)]
        #cmap = lambda x: (x, 1-x, 0)
        cmap = plt.get_cmap('prism')
        #color_list = [cmap(mx/nMatches) for mx in xrange(nMatches)]
        colors = distinct_colors(nMatches)
        pt2_args = dict(pts=draw_pts, ell=False, pts_color=BLACK, pts_size=8)
        pts_args = dict(pts=draw_pts, ell=False, pts_color=ORANGE, pts_size=6,
                        color_list=add_alpha(colors))
        ell_args = dict(ell=draw_ell, pts=False, color_list=colors)
        # Draw matching ellipses
        offset=(woff,hoff)
        def _drawkpts(**kwargs):
            draw_kpts2(kpts1[fm[:,0]], **kwargs)
            draw_kpts2(kpts2[fm[:,1]], offset=offset, **kwargs)
        def _drawlines(**kwargs):
            draw_matches2(kpts1, kpts2, fm, fs, kpts2_offset=offset, **kwargs)
        # Draw matching lines
        if draw_ell:
            _drawkpts(**ell_args)
        if draw_lines:
            _drawlines(color_list=colors)
        if draw_pts: 
            #_drawkpts(**pts_args)
            acolors = add_alpha(colors)
            pts_args.update(dict(pts_size=6, color_list=acolors))
            _drawkpts(**pt2_args)
            _drawkpts(**pts_args)

    return fig, ax

def deterministic_shuffle(list_):
    randS = int(np.random.rand()*np.uint(0-2)/2)
    np.random.seed(len(list_))
    np.random.shuffle(list_)
    np.random.seed(randS)

def distinct_colors(N):
    # http://blog.jianhuashao.com/2011/09/generate-n-distinct-colors.html
    import colorsys
    sat = .878
    val = .878
    HSV_tuples = [(x*1.0/N, sat, val) for x in xrange(N)]
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    deterministic_shuffle(RGB_tuples)
    return RGB_tuples

def add_alpha(colors):
    return [list(color)+[1] for color in colors]

def show_matches_annote_res(res, hs, cx,
                            fignum=None, 
                            plotnum=None,
                            title_aug=None, 
                            **kwargs):
    '''
    Wrapper for show_matches_annote
    '''
    qcx = res.qcx
    cx2_score = res.get_cx2_score()
    cx2_fm    = res.get_cx2_fm()
    cx2_fs    = res.get_cx2_fs()
    title_suff = None
    return show_matches_annote(hs, qcx, cx2_score, cx2_fm, cx2_fs, cx,
                         fignum, plotnum, title_aug, title_suff, **kwargs)

# TODO: This should go in viz
def show_matches_annote(hs, qcx, cx2_score, 
                        cx2_fm, cx2_fs, cx,
                        fignum=None, plotnum=None, 
                        title_pref=None, 
                        title_suff=None,
                        show_cx=False,
                        show_cid=True,
                        show_gname=True,
                        showTF=True,
                        showScore=True,
                        **kwargs):
    ' Shows matches with annotations '
    printDBG('[df2] Showing matches from %s in fignum=%r' % (hs.vs_str(cx, qcx), fignum))
    if np.isnan(cx):
        nan_img = np.zeros((100,100), dtype=np.uint8)
        title='(qx%r v NAN)' % (qcx)
        imshow(nan_img,fignum=fignum,plotnum=plotnum,title=title)
        return 
    # Read query and result info (chips, names, ...)
    rchip1, rchip2 = hs.get_chip([qcx, cx])
    kpts1, kpts2   = hs.get_kpts([qcx, cx])
    score = cx2_score[cx]
    fm = cx2_fm[cx]; fs = cx2_fs[cx]
    # Build the title string
    isgt_str  = hs.is_true_match_str(qcx, cx)
    title = ''
    if showTF:
        title += '*' + isgt_str  + '*'
    if showScore:
        score_str = (' score='+helpers.num_fmt(score)) % (score)
        title += score_str
    if not title_pref is None: title = title_pref + title
    if not title_suff is None: title = title + title_suff
    # Draw the matches
    fig, ax = show_matches2(rchip1, rchip2, kpts1, kpts2, fm, fs, 
                            fignum=fignum, plotnum=plotnum,
                            title=title, **kwargs)
    upperright_text(hs.vs_str(qcx, cx))
    # Finish annotations
    if   isgt_str == hs.UNKNOWN_STR: draw_border(ax, WHITE, 4)
    elif isgt_str == hs.TRUE_STR:    draw_border(ax, GREEN, 4)
    elif isgt_str == hs.FALSE_STR:   draw_border(ax, RED, 4)
    if show_gname:
        ax.set_xlabel(hs.get_gname(cx), fontproperties=FONTS.xlabel)
    return ax

def show_img(hs, cx, **kwargs):
    # Get the chip roi
    roi = hs.get_roi(roi)
    (rx,ry,rw,rh) = roi
    rxy = (rx,ry)
    # Get the image
    img = hs.get_image(gx)
    # Draw image
    imshow(img, **kwargs)
    # Draw ROI
    ax = plt.gca()
    bbox = matplotlib.patches.Rectangle(rxy,rw,rh) 
    bbox_color = [1, 0, 0]
    bbox.set_fill(False)
    bbox.set_edgecolor(bbox_color)
    ax.add_patch(bbox)

def show_keypoints(rchip,kpts,fignum=0,title=None, **kwargs):
    imshow(rchip,fignum=fignum,title=title,**kwargs)
    draw_kpts2(kpts)

def show_chip(hs, cx=None, allres=None, res=None, info=True, draw_kpts=True,
              nRandKpts=None, kpts_alpha=None, prefix='', **kwargs):
    if not res is None:
        cx = res.qcx
    if not allres is None:
        res = allres.qcx2_res[cx]
    rchip1    = hs.get_chip(cx)
    title_str = prefix + hs.cxstr(cx)
    # Add info to title
    if info: 
        title_str += ', '+hs.num_indexed_gt_str(cx)
    fig, ax = imshow(rchip1, title=title_str, **kwargs)
    if not res is None: 
        gname = hs.get_gname(cx)
        ax.set_xlabel(gname, fontproperties=FONTS.xlabel)
    if not draw_kpts:
        return
    kpts1  = hs.get_kpts(cx)
    kpts_args = dict(offset=(0,0), ell_linewidth=1.5, ell=True, pts=False)
    # Draw keypoints with groundtruth information
    if not res is None:
        gt_cxs = hs.get_other_indexed_cxs(cx)
        # Get keypoint indexes
        def stack_unique(fx_list):
            try:
                if len(fx_list) == 0:
                    return np.array([], dtype=int)
                stack_list = np.hstack(fx_list)
                stack_ints = np.array(stack_list, dtype=int)
                unique_ints = np.unique(stack_ints)
                return unique_ints
            except Exception as ex:
                 # debug in case of exception (seem to be happening)
                 print('==============')
                 print('Ex: %r' %ex)
                 print('----')
                 print('fx_list = %r ' % fx_list)
                 print('----')
                 print('stack_insts = %r' % stack_ints)
                 print('----')
                 print('unique_ints = %r' % unique_ints)
                 print('==============')
                 print(unique_ints)
                 raise
        all_fx = np.arange(len(kpts1))
        cx2_fm = res.get_cx2_fm()
        fx_list1 = [fm[:,0] for fm in cx2_fm]
        fx_list2 = [fm[:,0] for fm in cx2_fm[gt_cxs]] if len(gt_cxs) > 0 else np.array([])
        matched_fx = stack_unique(fx_list1)
        true_matched_fx = stack_unique(fx_list2)
        noise_fx = np.setdiff1d(all_fx, matched_fx)
        # Print info
        print('[df2] %s has %d keypoints. %d true-matching. %d matching. %d noisy.' %
             (hs.cxstr(cx), len(all_fx), len(true_matched_fx), len(matched_fx), len(noise_fx)))
        # Get keypoints
        kpts_true  = kpts1[true_matched_fx]
        kpts_match = kpts1[matched_fx, :]
        kpts_noise = kpts1[noise_fx, :]
        # Draw keypoints
        legend_tups = []
        # helper function taking into acount phantom labels
        def _kpts_helper(kpts_, color, alpha, label):
            draw_kpts2(kpts_, ell_color=color, ell_alpha=alpha, **kpts_args)
            phant_ = Circle((0, 0), 1, fc=color)
            legend_tups.append((phant_, label))
        _kpts_helper(kpts_noise,   RED, .1, 'Unverified')
        _kpts_helper(kpts_match,  BLUE, .4, 'Verified')
        _kpts_helper(kpts_true,  GREEN, .6, 'True Matches')
        #plt.legend(*zip(*legend_tups), framealpha=.2)
    # Just draw boring keypoints
    else:
        if kpts_alpha is None: 
            kpts_alpha = .4
        if not nRandKpts is None: 
            nkpts1 = len(kpts1)
            fxs1 = np.arange(nkpts1)
            size = nRandKpts
            replace = False
            p = np.ones(nkpts1)
            p = p / p.sum()
            fxs_randsamp = np.random.choice(fxs1, size, replace, p)
            kpts1 = kpts1[fxs_randsamp]
            ax = plt.gca()
            ax.set_xlabel('displaying %r/%r keypoints' % (nRandKpts, nkpts1), fontproperties=FONTS.xlabel)
            # show a random sample of kpts
        draw_kpts2(kpts1, ell_alpha=kpts_alpha, ell_color=RED, **kpts_args)

def show_topN_matches(hs, res, N=5, fignum=4): 
    figtitle = ('q%s -- TOP %r' % (hs.cxstr(res.qcx), N))
    topN_cxs = res.topN_cxs(N)
    max_nCols = max(5,N)
    _show_chip_matches(hs, res, topN_cxs=topN_cxs, figtitle=figtitle, 
                       fignum=fignum, all_kpts=False)

def show_gt_matches(hs, res, fignum=3): 
    figtitle = ('q%s -- GroundTruth' % (hs.cxstr(res.qcx)))
    gt_cxs = hs.get_other_indexed_cxs(res.qcx)
    max_nCols = max(5,len(gt_cxs))
    _show_chip_matches(hs, res, gt_cxs=gt_cxs, figtitle=figtitle, 
                       fignum=fignum, all_kpts=True)

def show_match_analysis(hs, res, N=5, fignum=3, figtitle='', show_query=True,
                        annotations=True, compare_cxs=None, q_cfg=None, **kwargs):
    if not compare_cxs is None:
        topN_cxs = compare_cxs
        figtitle = 'comparing to '+hs.cxstr(topN_cxs) + figtitle
    else:
        topN_cxs = res.topN_cxs(N, q_cfg)
        if len(topN_cxs) == 0: 
            warnings.warn('len(topN_cxs) == 0')
            figtitle = 'WARNING: no top scores!' + hs.cxstr(res.qcx)
        else:
            topscore = res.get_cx2_score()[topN_cxs][0]
            figtitle = ('topscore=%r -- q%s' % (topscore, hs.cxstr(res.qcx))) + figtitle
    all_gt_cxs = hs.get_other_indexed_cxs(res.qcx)
    missed_gt_cxs = np.setdiff1d(all_gt_cxs, topN_cxs)
    max_nCols = min(5,N)
    return _show_chip_matches(hs, res,
                              gt_cxs=missed_gt_cxs, 
                              topN_cxs=topN_cxs,
                              figtitle=figtitle,
                              max_nCols=max_nCols,
                              show_query=show_query,
                              fignum=fignum,
                              annotations=annotations,
                              q_cfg=q_cfg,
                              **kwargs)

def _show_chip_matches(hs, res, figtitle='', max_nCols=5,
                       topN_cxs=None, gt_cxs=None, show_query=False,
                       all_kpts=False, fignum=3, annotations=True, q_cfg=None,
                       split_plots=False, **kwargs):
    ''' Displays query chip, groundtruth matches, and top 5 matches'''
    #print('========================')
    #print('[df2] Show chip matches:')
    if topN_cxs is None: topN_cxs = []
    if gt_cxs is None: gt_cxs = []
    print('[df2]----------------')
    print('[df2] #top=%r #missed_gts=%r' % (len(topN_cxs),len(gt_cxs)))
    print('[df2] * max_nCols=%r' % (max_nCols,))
    print('[df2] * show_query=%r' % (show_query,))
    ranked_cxs = res.topN_cxs('all', q_cfg=q_cfg)
    annote = annotations
    # Build a subplot grid
    nQuerySubplts = 1 if show_query else 0
    nGtSubplts = nQuerySubplts + (0 if gt_cxs is None else len(gt_cxs))
    nTopNSubplts  = 0 if topN_cxs is None else len(topN_cxs)
    nTopNCols = min(max_nCols, nTopNSubplts)
    nGTCols   = min(max_nCols, nGtSubplts)
    if not split_plots:
        nGTCols = max(nGTCols, nTopNCols)
        nTopNCols = nGTCols
    nGtRows   = int(np.ceil(nGtSubplts / nGTCols))
    nTopNRows = int(np.ceil(nTopNSubplts / nTopNCols))
    nGtCells = nGtRows * nGTCols
    nTopNCells = nTopNRows * nTopNCols
    if split_plots:
        nRows = nGtRows
    else:
        nRows = nTopNRows+nGtRows
    # Helper function for drawing matches to one cx
    def show_matches_(cx, orank, plotnum):
        aug = 'rank=%r ' % orank
        printDBG('[df2] plotting: %r'  % (plotnum,))
        kwshow  = dict(draw_ell=annote, draw_pts=annote, draw_lines=annote,
                       ell_alpha=.5, all_kpts=all_kpts, **kwargs)
        show_matches_annote_res(res, hs, cx, title_aug=aug, plotnum=plotnum, **kwshow)
    def plot_query(plotx_shift, rowcols):
        printDBG('Plotting Query:')
        plotx = plotx_shift + 1
        plotnum = (rowcols[0], rowcols[1], plotx)
        printDBG('[df2] plotting: %r' % (plotnum,))
        show_chip(hs, res=res, plotnum=plotnum, draw_kpts=annote, prefix='query ')
    # Helper to draw many cxs
    def plot_matches_cxs(cx_list, plotx_shift, rowcols):
        if cx_list is None: return
        for ox, cx in enumerate(cx_list):
            plotx = ox + plotx_shift + 1
            plotnum = (rowcols[0], rowcols[1], plotx)
            oranks = np.where(ranked_cxs == cx)[0]
            if len(oranks) == 0:
                orank = -1
                continue
            orank = oranks[0] + 1
            show_matches_(cx, orank, plotnum)

    query_uid = res.query_uid
    query_uid = re.sub(r'_trainID\([0-9]*,........\)','', query_uid)
    query_uid = re.sub(r'_indxID\([0-9]*,........\)','', query_uid)
    query_uid = re.sub(r'_dcxs\(........\)','', query_uid)

    fig = figure(fignum=fignum); fig.clf()
    plt.subplot(nRows, nGTCols, 1)
    # Plot Query
    if show_query: 
        plot_query(0, (nRows, nGTCols))
    # Plot Ground Truth
    plot_matches_cxs(gt_cxs, nQuerySubplts, (nRows, nGTCols)) 
    # Plot TopN in a new figure
    if split_plots:
        set_figtitle(figtitle+'GT', query_uid)
        nRows = nTopNRows
        fig = figure(fignum=fignum+9000); fig.clf()
        plt.subplot(nRows, nTopNCols, 1)
        shift_topN = 0
    else:
        shift_topN = nGtCells
    plot_matches_cxs(topN_cxs, shift_topN, (nRows, nTopNCols))
    if split_plots:
        set_figtitle(figtitle+'topN', query_uid)
    else:
        set_figtitle(figtitle, query_uid)
    print('-----------------')
    return fig

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    print('=================================')
    print('[df2] __main__ = draw_func2.py')
    print('=================================')
    from __init__ import *
    qcx = 0
    hs = ld2.HotSpotter()
    hs.load_tables(ld2.DEFAULT)
    hs.load_chips()
    hs.load_features()
    hs.set_samples()
    res = mc2.build_result_qcx(hs, qcx)
    print('')
    print('''
    exec(open("draw_func2.py").read())
    ''')
    N=5
    df2.rrr()
    figtitle='q%s -- Analysis' % (hs.cxstr(res.qcx),)
    topN_cxs = res.topN_cxs(N)
    all_gt_cxs = hs.get_other_indexed_cxs(res.qcx)
    gt_cxs = np.setdiff1d(all_gt_cxs, topN_cxs)
    max_nCols = max(5,N)
    fignum=3
    show_query = True
    all_kpts = False
    #get_geometry(1)
    df2.show_match_analysis(hs, res, N)
    df2.update()
    exec(df2.present())
