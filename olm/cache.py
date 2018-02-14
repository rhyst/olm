import pickle
import time
import os
import hashlib
from olm.logger import get_logger
from olm.constants import CacheTypes

logger = get_logger('olm.cache')

def hash_object(thing):
    m = hashlib.md5()
    string = pickle.dumps(thing)
    m.update(string)
    return m.hexdigest()

def check_cache(CONTEXT, files):
    time_start = time.time()
    if not CONTEXT.caching_enabled:
        logger.info('Caching disabled')
        return

    old_hashes = {}
    CONTEXT['is_cached'] = False
    if os.path.isfile(CONTEXT.CACHE_LOCATION):
        with open(CONTEXT.CACHE_LOCATION, 'rb') as handle:
            old_hashes = pickle.load(handle)
            CONTEXT['is_cached'] = True

    hashes = {}
    changes = []
    for afile in files:
        if 'cache_id' in dir(afile):
            m = hashlib.md5()
            id_hash = hash_object(afile.cache_id)
            meta_hash = hash_object(afile.metadata)
            content_hash = hash_object(afile.content)
            hashes[id_hash] = (meta_hash, content_hash)

            if afile.output_filepath is None:
                identifier = afile.basename
            else:
                identifier = afile.output_filepath
            if id_hash in old_hashes:
                if old_hashes[id_hash][0] != meta_hash:
                    logger.info('{} metadata is different to cache'.format(identifier))
                    change = '{}.{}'.format(afile.cache_type, CacheTypes.META_CHANGE)
                    if change not in changes:
                        changes.append(change)
                if old_hashes[id_hash][1] != content_hash:
                    logger.info('{} content is different to cache'.format(identifier))
                    change = '{}.{}'.format(afile.cache_type, CacheTypes.CONTENT_CHANGE)
                    if change not in changes:
                        changes.append(change)
                if old_hashes[id_hash][0] == meta_hash and old_hashes[id_hash][1] == content_hash:
                    afile.same_as_cache = True
            else:
                change = '{}.{}'.format(afile.cache_type, CacheTypes.NEW_FILE)
                logger.info('{} is a new file'.format(identifier))
                if change not in changes:
                    changes.append(change)

    CONTEXT['cache_change_types'] = changes

    with open(CONTEXT.CACHE_LOCATION, 'wb') as handle:
        pickle.dump(hashes, handle, protocol=pickle.HIGHEST_PROTOCOL)

    CONTEXT['cache'] = hashes
    
    logger.info('Cache finished in %.3f', time.time() - time_start)

def has_file_changed(CONTEXT, file):
    pass