import pickle
import time
import os
import hashlib
from olm.logger import get_logger
from olm.constants import CacheTypes, ArticleStatus
from collections import namedtuple

logger = get_logger('olm.cache')

def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added_keys = d1_keys - d2_keys
    removed_keys = d2_keys - d1_keys
    modified = {o: (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    added = {}
    removed = {}
    for key in added_keys:
        added[key] = d1[key]
    for key in removed_keys:
        removed[key] = d2[key]
    comparison = namedtuple('comparison', ['added', 'removed', 'modified'])
    return comparison(added, removed, modified)

def hash_object(thing):
    m = hashlib.md5()
    string = pickle.dumps(thing)
    m.update(string)
    return m.hexdigest()

def add_change(afile, change_list, file_type, change_type):
    change = '{}.{}'.format(file_type, change_type)
    if change not in change_list:
        if afile.status != ArticleStatus.DRAFT:
            change_list.append(change)
    return change_list

def check_cache(CONTEXT, files):
    time_start = time.time()
    if not CONTEXT.caching_enabled:
        logger.info('Caching disabled')
        return
    
    # Load the cache file
    old_hashes = {}
    CONTEXT['is_cached'] = False
    if os.path.isfile(CONTEXT.CACHE_LOCATION):
        with open(CONTEXT.CACHE_LOCATION, 'rb') as handle:
            old_hashes = pickle.load(handle)
            CONTEXT['is_cached'] = True

    hashes       = {} # New hashes to be saved to cache file
    changes      = [] # List of change types
    meta_changes = [] # List of all changed metadata
    for afile in files:
        if 'cache_id' not in dir(afile):
            continue
        # Get hashes of id and content
        m               = hashlib.md5()
        id_hash         = hash_object(afile.cache_id)
        meta_hash       = hash_object(afile.metadata)
        content_hash    = hash_object(afile.content)
        hashes[id_hash] = (meta_hash, content_hash, afile.metadata)

        # Figure out an identifier for logging
        if afile.output_filepath is None:
            identifier = afile.basename
        else:
            identifier = afile.output_filepath
        
        # If the id hash exists in the old hashes check for changes
        # else add new file change
        if id_hash in old_hashes:
            # If difference is in metadata compile a diff object for the metadata
            # and store it along with a meta change
            if old_hashes[id_hash][0] != meta_hash:
                logger.info('{} metadata is different to cache'.format(identifier))
                if afile.status != ArticleStatus.DRAFT and afile.status:
                    diff = dict_compare(old_hashes[id_hash][2], afile.metadata)
                    meta_changes.append(diff)
                changes = add_change(afile, changes, afile.cache_type, CacheTypes.META_CHANGE)
            # If difference in content then just add a content change
            if old_hashes[id_hash][1] != content_hash:
                logger.info('{} content is different to cache'.format(identifier))
                changes = add_change(afile, changes, afile.cache_type, CacheTypes.CONTENT_CHANGE)
            # If same mark the file as same_as_cache so it doesnt get written
            if old_hashes[id_hash][0] == meta_hash and old_hashes[id_hash][1] == content_hash:
                afile.same_as_cache = True
        else:
            logger.info('{} is a new file'.format(identifier))
            changes = add_change(afile, changes, afile.cache_type, CacheTypes.NEW_FILE)
            meta_changes.append(afile.metadata)

    logger.debug('{} are the new changes'.format(changes))
    CONTEXT['cache_change_types'] = changes
    CONTEXT['cache_changed_meta'] = meta_changes
   
    # Write the latest build's caches to file
    with open(CONTEXT.CACHE_LOCATION, 'wb') as handle:
        pickle.dump(hashes, handle, protocol=pickle.HIGHEST_PROTOCOL)

    CONTEXT['cache'] = hashes
    logger.info('Cache finished in %.3f', time.time() - time_start)