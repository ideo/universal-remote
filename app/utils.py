import yaml
import bz2
import _pickle as cPickle


def load_yaml_file(filepath):
    with open(filepath, encoding="utf8") as file:
        obj = yaml.load(file, Loader=yaml.loader.SafeLoader)
    return obj


def save_gherkin(data, filepath):
    """
    A compressed pickle file - a little pickle!
    Saves a .pbz2 files. This will expect that file extension.
    """
    with bz2.BZ2File(filepath, "w") as write_file: 
        cPickle.dump(data, write_file)


def load_gherkin(filepath):
    """
    A compressed pickle file - a little pickle!
    Loads a .pbz2 files. This will expect that file extension.
    """
    data = bz2.BZ2File(filepath, "rb")
    data = cPickle.load(data)
    return data