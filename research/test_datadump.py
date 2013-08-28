import datetime
import timeit
import numpy as np
import cPickle
import pickle
import hotspotter.helpers as helpers

data1 = (255 * np.random.rand(10000,10000)).astype(np.uint8)
data2 = np.random.rand(10000,10000).astype(np.float64)
data3 = (255 * np.random.rand(10000,10000)).astype(np.int32)

print('Created arrays')

# --- Saving ---
def save_npy(fpath, data):
    with open(fpath, 'wb') as file:
        np.save(file, data)
def save_npz(fpath, data):
    with open(fpath, 'wb') as file:
        np.savez(file, data)
def save_cPkl(fpath, data):
    with open(fpath, 'wb') as file:
        cPickle.dump(data, file, cPickle.HIGHEST_PROTOCOL)
def save_pkl(fpath, data):
    with open(fpath, 'wb') as file:
        pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)
# --- ---

# --- Loading ---
def load_npz(fpath):
    with open(fpath, 'rb') as file:
        npz = np.load(file, mmap_mode=None)
        data = npz['arr_0']
        npz.close()
    return data
def load_npz_memmap(fpath):
    with open(fpath, 'rb') as file:
        npz = np.load(file, mmap_mode='r')
        data = npz['arr_0']
        npz.close()
    return data
def load_npy(fpath):
    with open(fpath, 'rb') as file:
        data = np.load(file)
def load_cPkl(fpath):
    with open(fpath, 'rb') as file:
        return cPickle.load(file)
def load_pkl(fpath):
    with open(fpath, 'rb') as file:
        return pickle.load(file)
# --- ---

save_npy.ext = '.npy'
save_npz.ext = '.npz'
save_cPkl.ext = '.cPkl'
save_pkl.ext = '.pkl'

load_npy.ext = '.npy'
load_npz.ext = '.npz'
load_cPkl.ext = '.cPkl'
load_pkl.ext = '.pkl'


fpath_list = ['data1','data2','data3']
data_list  =  [data1, data2, data3]

save_func_list = [save_npy, save_npz, save_cPkl, save_pkl]
load_func_list = [load_npy, load_npz, load_cPkl, load_pkl]

fpath = '/media/Store/data/work/Oxford_Buildings/.hs_internals/'

# Test Save
for save_func in save_func_list:
    print('Testing: '+save_func.__name__)
    print(' withext: '+save_func.ext)
    tt_total = helpers.tic(save_func.__name__)

    for fpath, data, in zip(fpath_list, data_list):
        fpath += save_func.ext
        tt_single = helpers.tic(fpath)
        save_func(fpath, data)
        helpers.toc(tt_single)
    helpers.toc(tt_total)
    print('------------------')

# Test memory:
for save_func in save_func_list:
    for fpath in fpath_list:
        fpath += save_func.ext
        print(helpers.file_megabytes_str(fpath))

# Test Load
for load_func in load_func_list:
    print('Testing: '+load_func.__name__)
    print(' withext: '+load_func.ext)
    tt_total = helpers.tic(load_func.__name__)

    for fpath, data, in zip(fpath_list, data_list):
        fpath += load_func.ext
        tt = helpers.tic(fpath)
        data2 = load_func(fpath)
        helpers.toc(tt)
    helpers.toc(tt_total)
    print('------------------')


fpath = ld2.OXFORD+'/.hs_internals/computed/cache/cx2_desc_HESAFF_szorig.npz'
fpath_py = ld2.OXFORD+'/.hs_internals/computed/cache/cx2_desc_HESAFF_szorig.npy'
fpath_pyz = ld2.OXFORD+'/.hs_internals/computed/cache/cx2_desc_TEMP.npz'


print(helpers.file_megabytes_str(fpath))

tic = helpers.tic
toc = helpers.toc

#tt = tic(fpath_py)
#with open(fpath, 'wb') as file_:
    #npz = np.load(file_, fpath)
    #data = npz['arr_0']
    #npz.close()
#toc(tt)

tt = tic(fpath_py)
with open(fpath_py, 'wb') as file_:
    np.save(file_, data)
toc(tt)

tt = tic(fpath_pyz)
with open(fpath_pyz, 'wb') as file_:
    np.savez(file_, data)
toc(tt)

tt = tic(fpath_py)
with open(fpath_py, 'rb') as file_:
    npy_data = np.load(file_)
toc(tt)
print(helpers.file_megabytes_str(fpath_py))


tt = tic(fpath_pyz)
with open(fpath_pyz, 'rb') as file_:
    npz = np.load(file_)
    npz_data = npz['arr_0']
    npz.close()
toc(tt)
print(helpers.file_megabytes_str(fpath_pyz))

tt = tic(fpath_pyz)
with open(fpath_pyz, 'rb') as file_:
    npz = np.load(file_, mmap_mode='r+')
    npz_data = npz['arr_0']
    npz.close()
toc(tt)

tt = helpers.tic(fpath)
data2 = load_func(fpath)

with Timer():
    with open(fpath, 'rb') as file_:
        npz = np.load(file_, mmap_mode='r')
        data = npz['arr_0']
        npz.close()

with Timer():
    with open(fpath, 'rb') as file_:
        npz2 = np.load(file_, mmap_mode=None)
        data2 = npz['arr_0']
        npz2.close()
