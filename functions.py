

from abydos import distance
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





def removeConsecutiveDuplicates(name, k):
    while True:
        count = 0
        chars = set(name)
        for c in chars:
            if c * k in name:
                name = name.replace(c * k, c)
                count += 1
        if count == 0:
            break
    return name



def add_values_in_dict(sample_dict, key, list_of_values):

    ''' Append multiple values to a key in
        the given dictionary '''
    if key not in sample_dict and len(list_of_values) != 0:
        sample_dict[key] = list()
        # if len(list_of_values) != 0:
        sample_dict[key].extend(list_of_values)
    return sample_dict