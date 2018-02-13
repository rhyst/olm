import pyhash
import pickle
import time
import os
from olm.logger import get_logger

logger = get_logger('olm.cache')

def file_check(CONTEXT, files):
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
            hasher = pyhash.fnv1_32()
            id_hash = hasher(afile.cache_id)
            meta_hash = str(hasher(pickle.dumps(afile.metadata)))
            content_hash = str(hasher(afile.content))
            full_hash = meta_hash + content_hash
            hashes[id_hash] = full_hash

            if id_hash in old_hashes:
                if old_hashes[id_hash] != full_hash:
                    logger.info('{} is different to cache'.format(afile.output_filepath))
                else:
                    afile.same_as_cache = True

    with open(CONTEXT.CACHE_LOCATION, 'wb') as handle:
        pickle.dump(hashes, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    logger.info('Cache finished in %.3f', time.time() - time_start)