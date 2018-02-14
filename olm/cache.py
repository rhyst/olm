import pickle
import time
import os
from olm.logger import get_logger
import hashlib

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
    try:
        with open(CONTEXT.CACHE_LOCATION, 'rb') as handle:
            old_hashes = pickle.load(handle)
            CONTEXT['is_cached'] = True
    except FileNotFoundError:
        CONTEXT['is_cached'] = False
        old_hashes = {}

    hashes = {}
    for afile in files:
        if 'cache_id' in dir(afile):
            m = hashlib.md5()
            id_hash = hash_object(afile.cache_id)
            meta_hash = hash_object(afile.metadata)
            content_hash = hash_object(afile.content)
            hashes[id_hash] = (meta_hash, content_hash)

            if id_hash in old_hashes:
                if old_hashes[id_hash][0] != meta_hash:
                    logger.info('{} metadata is different to cache'.format(afile.output_filepath))
                if old_hashes[id_hash][1] != content_hash:
                    logger.info('{} content is different to cache'.format(afile.output_filepath))
                if old_hashes[id_hash][0] == meta_hash and old_hashes[id_hash][1] == content_hash:
                    afile.same_as_cache = True
            else:
                pass
                # new file

    with open(CONTEXT.CACHE_LOCATION, 'wb') as handle:
        pickle.dump(hashes, handle, protocol=pickle.HIGHEST_PROTOCOL)

    CONTEXT['cache'] = hashes
    
    logger.info('Cache finished in %.3f', time.time() - time_start)

def has_file_changed(CONTEXT, file):
    pass