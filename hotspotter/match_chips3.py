from __future__ import division, print_function
from hscom import __common__
(print, print_, print_on, print_off,
 rrr, profile, printDBG) = __common__.init(__name__, '[mc3]', DEBUG=False)
# Python
import re
# HotSpotter
from hscom import params
from hscom import helpers as util
import DataStructures as ds
import matching_functions as mf

# TODO INTEGRATE INDENTER 2 better
import HotSpotterAPI as api
from hscom import Parallelize as parallel
modules = [api, api.fc2, api.cc2, parallel, mf, ds]


@profile
@util.indent_decor('[nn_index]')
def ensure_nn_index(hs, qdat, dcxs):
    print('checking flann')
    # NNIndexes depend on the data cxs AND feature / chip configs
    printDBG('qdat=%r' % (qdat,))
    printDBG('dcxs=%r' % (dcxs,))

    feat_uid = qdat.cfg._feat_cfg.get_uid()
    dcxs_uid = util.hashstr_arr(dcxs, 'dcxs') + feat_uid
    if not dcxs_uid in qdat._dcxs2_index:
        # Make sure the features are all computed first
        print('[mc3] qdat.flann[dcxs_uid]... nn_index cache miss')
        print('[mc3] dcxs_ is not in qdat cache')
        print('[mc3] hashstr(dcxs_) = %r' % dcxs_uid)
        print('[mc3] REFRESHING FEATURES')
        hs.refresh_features(dcxs)
        # Compute the FLANN Index
        data_index = ds.NNIndex(hs, dcxs)
        qdat._dcxs2_index[dcxs_uid] = data_index
    else:
        print('[mc3] qdat.flann[dcxs_uid]... cache hit')
    qdat._data_index = qdat._dcxs2_index[dcxs_uid]


#----------------------
# Convinience Functions
#----------------------

# QUERY PREP FUNCTIONS
@util.indent_decor('[prep-request]')
def prep_query_request(hs, qdat=None, query_cfg=None, qcxs=None, dcxs=None, **kwargs):
    printDBG('prep_query_request ---------------')
    printDBG('hs=%r' % hs)
    printDBG('query_cfg=%r' % query_cfg)
    printDBG('qdat=%r' % qdat)
    printDBG('dcxs=%r' % dcxs)
    printDBG('qcxs=%r' % qcxs)
    printDBG('[mc3]---------------')
    if dcxs is None:
        # Use all database indexes if not specified
        dcxs = hs.get_indexed_sample()
    if qdat is None:
        # Use the hotspotter query data if the user does not provide one
        qdat = hs.qdat
        qdat._dcxs = dcxs
    if query_cfg is None:
        # Use the hotspotter query_cfg if the user does not provide one
        #hs.assert_prefs()
        query_cfg = hs.prefs.query_cfg
    if len(kwargs) > 0:
        # Update any arguments in the query config based on kwargs
        query_cfg = query_cfg.deepcopy(**kwargs)
    assert not isinstance(query_cfg, list)
    qdat.set_cfg(query_cfg, hs=hs)
    if qcxs is None:
        raise AssertionError('please query an index')
    if len(dcxs) == 0:
        raise AssertionError('please select database indexes')
    printDBG('qcxs=%r' % qcxs)
    printDBG('dcxs=%r' % dcxs)
    qdat._qcxs = qcxs
    qdat._dcxs = dcxs
    #---------------
    # Flip if needebe
    query_type = qdat.cfg.agg_cfg.query_type
    if query_type == 'vsone':
        (dcxs, qcxs) = (qdat._qcxs, qdat._dcxs)
    elif query_type == 'vsmany':
        (dcxs, qcxs) = (qdat._dcxs, qdat._qcxs)
    else:
        raise AssertionError('Unknown query_type=%r' % query_type)
    return qdat


# QUERY EXEC FUNCTIONS
@util.indent_decor('[prequery]')
def prequery_checks(hs, qdat, qcxs=None, dcxs=None):
    # Checks that happen JUST before querytime
    dcxs = dcxs if dcxs is not None else qdat._dcxs
    qcxs = qcxs if qcxs is not None else qdat._qcxs
    query_cfg = qdat.cfg
    query_uid = qdat.cfg.get_uid('noCHIP')
    feat_uid = qdat.cfg._feat_cfg.get_uid()
    query_hist_id = (feat_uid, query_uid)

    def _refresh(hs, qdat, unload=False):
        print('_refresh, unload=%r' % unload)
        if unload:
            #print('[mc3] qdat._dcxs = %r' % qdat._dcxs)
            hs.unload_cxdata('all')
            # Reload
            qdat = prep_query_request(hs, query_cfg=query_cfg, qcxs=qcxs, dcxs=dcxs)
        ensure_nn_index(hs, qdat, qdat._dcxs)

    print('checking')
    if hs.query_history[-1][0] is None:
        # FIRST LOAD:
        print('[mc3] FIRST LOAD. Need to reload features')
        print('[mc3] ensuring nn index')
        _refresh(hs, qdat, unload=hs.dirty)
    if hs.query_history[-1][0] != feat_uid:
        print('[mc3] FEAT_UID is different. Need to reload features')
        print('[mc3] Old: ' + str(hs.query_history[-1][0]))
        print('[mc3] New: ' + str(feat_uid))
        _refresh(hs, qdat, True)
    if hs.query_history[-1][1] != query_uid:
        print('[mc3] QUERY_UID is different. Need to refresh features')
        print('[mc3] Old: ' + str(hs.query_history[-1][1]))
        print('[mc3] New: ' + str(query_uid))
        _refresh(hs, qdat, False)
    print('checked')
    hs.query_history.append(query_hist_id)
    print('[mc3] prequery(): query_uid = %r ' % query_uid)


# OTHER

def make_nn_index(hs, sx2_cx=None):
    if sx2_cx is None:
        sx2_cx = hs.indexed_sample_cx
    data_index = ds.NNIndex(hs, sx2_cx)
    return data_index


def simplify_test_uid(test_uid):
    # Remove extranious characters from test_uid
    #test_uid = re.sub(r'_trainID\([0-9]*,........\)','', test_uid)
    #test_uid = re.sub(r'_indxID\([0-9]*,........\)','', test_uid)
    test_uid = re.sub(r'_dcxs([^)]*)', '', test_uid)
    #test_uid = re.sub(r'HSDB_zebra_with_mothers','', test_uid)
    #test_uid = re.sub(r'GZ_ALL','', test_uid)
    #test_uid = re.sub(r'_sz750','', test_uid)
    #test_uid = re.sub(r'_FEAT([^(]*)','', test_uid)
    #test_uid = test_uid.strip(' _')
    return test_uid


def load_cached_query(hs, qdat, aug_list=['']):
    qcxs = qdat._qcxs
    result_list = []
    for aug in aug_list:
        qcx2_res = mf.load_resdict(hs, qcxs, qdat, aug)
        if qcx2_res is None:
            return None
        result_list.append(qcx2_res)
    print('[mc3] ... query result cache hit')
    return result_list


#----------------------
# Main Query Logic
#----------------------
@profile
# Query Level 3
@util.indent_decor('[QL3-dcxs]')
def query_dcxs(hs, qcx, dcxs, qdat, dochecks=True):
    'wrapper that bypasses all that "qcx2_ map" buisness'
    print('[q3] query_dcxs()')
    result_list = execute_query_safe(hs, qdat, [qcx], dcxs)
    res = result_list[0].values()[0]
    return res


# Query Level 3
@util.indent_decor('[QL3-request]')
def process_query_request(hs, qdat, dochecks=True):
    'wrapper that bypasses all that "qcx2_ map" buisness'
    print('[q3] process_query_request()')
    if dochecks:
        prequery_checks(hs, qdat)
    dcxs = qdat._dcxs
    qcxs = qdat._qcxs
    qcxs = qdat._qcxs
    result_list = execute_query_safe(hs, qdat, qcxs, dcxs)
    res = result_list[0]
    return res


# Query Level 2
@util.indent_decor('[QL2-safe]')
def execute_query_safe(hs, qdat, qcxs, dcxs, use_cache=True):
    '''Executes a query, performs all checks, callable on-the-fly'''
    print('[execute_query_safe()]')
    qdat = prep_query_request(hs, qdat=qdat, qcxs=qcxs, dcxs=dcxs)
    prequery_checks(hs, qdat, qcxs, dcxs)
    return execute_cached_query(hs, qdat, qcxs, dcxs, use_cache=use_cache)


# Query Level 2
@util.indent_decor('[QL2-list]')
def query_list(hs, qcxs, dcxs=None, **kwargs):
    print('[query_list()]')
    qdat = prep_query_request(hs, qcxs=qcxs, dcxs=dcxs, **kwargs)
    qcx2_res = execute_cached_query(hs, qdat, qcxs, dcxs)[0]
    return qcx2_res


# Query Level 1
@util.indent_decor('[QL1]')
def execute_cached_query(hs, qdat, qcxs, dcxs, use_cache=True):
    # caching
    if not params.args.nocache_query and use_cache:
        result_list = load_cached_query(hs, qdat)
        if not result_list is None:
            return result_list
    print('[query_cached()]')
    ensure_nn_index(hs, qdat, dcxs)
    print('[mc3] qcxs=%r' % qdat._qcxs)
    print('[mc3] len(dcxs)=%r' % len(qdat._dcxs))
    print('[mc3] len(qdat._dcxs2_index)=%r' % len(qdat._dcxs2_index))
    if qdat._data_index is None:
        print('ERROR in execute_cached_query()')
        print('[mc3] qdat_dcxs2_index._dcxs2_index=%r' % len(qdat._dcxs2_index))
        print('[mc3] dcxs=%r' % dcxs)
        print('[mc3] qdat._dcxs2_index.keys()=%r' % qdat._dcxs2_index.keys())
        print('[mc3] qdat._data_index=%r' % qdat._data_index)
        raise Exception('Data index cannot be None at query time')
    # Do the actually query
    result_list = execute_query_fast(hs, qdat, qcxs, dcxs)
    for qcx2_res in result_list:
        for qcx, res in qcx2_res.iteritems():
            res.save(hs)
    return result_list


@profile
# Query Level 0
def execute_query_fast(hs, qdat, qcxs, dcxs):
    '''Executes a query and assumes qdat has all precomputed information'''
    # Nearest neighbors
    neighbs = mf.nearest_neighbors(hs, qcxs, qdat)
    # Nearest neighbors weighting and scoring
    weights, filt2_meta = mf.weight_neighbors(hs, neighbs, qdat)
    # Thresholding and weighting
    nnfiltFILT = mf.filter_neighbors(hs, neighbs, weights, qdat)
    # Nearest neighbors to chip matches
    matchesFILT = mf.build_chipmatches(hs, neighbs, nnfiltFILT, qdat)
    # Spatial verification
    matchesSVER = mf.spatial_verification(hs, matchesFILT, qdat)
    # Query results format
    result_list = [
        mf.chipmatch_to_resdict(hs, matchesSVER, filt2_meta, qdat),
    ]
    return result_list


#if __name__ == '__main__':
    #import multiprocessing
    #multiprocessing.freeze_support()
    #from hsviz import draw_func2 as df2
    #import dev
    ##exec(open('match_chips3.py').read())
    #df2.rrr()
    #df2.reset()
    #mf.rrr()
    #ds.rrr()
    #main_locals = dev.dev_main()
    #execstr = util.execstr_dict(main_locals, 'main_locals')
    #exec(execstr)
    ##df2.DARKEN = .5
    #df2.DISTINCT_COLORS = True
    #exec(df2.present())
