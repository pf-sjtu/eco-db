# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 14:03:50 2020

@author: PENG Feng
@email:  im.pengf@outlook.com
"""

import time, os, shutil, json, pickle


class Project:
    def __init__(self, name, dir=None, clear=False, verbose=False):
        self.set_verbose(verbose)
        self.name = name
        if type(dir) == str:
            self.dir = (dir + "/" + name).replace("\\", "/").replace("//", "/")
        else:
            self.dir = name
        if os.path.isdir(self.dir) and clear:
            self.remove()
            time.sleep(0.5)
        if not os.path.isdir(self.dir):
            os.mkdir(self.dir)

    def set_verbose(self, verbose):
        if type(verbose) == bool:
            self.verbose = verbose

    def listdir(self):
        return os.listdir(self.dir)

    def check_name(self, name):
        if name == "__name__":
            return self.name
        else:
            return name

    def log(self, msg, filename="__name__", encoding="utf-8"):
        filename = self.check_name(filename)
        filename = self.dir + "/" + filename.replace(".log", "") + ".log"
        prefix = time.strftime("%Y-%m-%d %H:%M:%S | ", time.localtime())
        with open(filename, "a", encoding=encoding) as f:
            f.write(prefix + msg + "\n")
        if self.verbose:
            print("log: " + msg)

    def json_dump(self, data, filename="__name__", msg=""):
        """
        Parameters
        ----------
        data : any
            Data to be dumped.
        filename : string, optional
            Name of the json file. The default is the name of the project.
        msg : string, optional
            Log message. The default is "".

        Returns
        -------
        None.

        """
        filename = self.check_name(filename)
        filename = self.dir + "/" + filename.replace(".json", "") + ".json"
        with open(filename, "w") as f:
            json.dump(data, f)
        self.log("json dump to " + filename + (". " + msg if len(msg) else "."))

    def json_load(self, filename="__name__", msg=""):
        """
        Parameters
        ----------
        filename : string, optional
            Name of the data file. The default is the name of the project.
        msg : string, optional
            Log message. The default is "".

        Returns
        -------
        data : any
        """
        filename = self.check_name(filename)
        filename = self.dir + "/" + filename.replace(".json", "") + ".json"
        with open(filename, "r") as f:
            data = json.load(f)
        if len(msg):
            self.log("json load from " + filename + ". " + msg)
        else:
            print("json load from " + filename + ". ")
        return data

    def pickle_dump(self, data, filename="__name__", msg=""):
        """
        Parameters
        ----------
        data : any
            Data to be dumped.
        filename : string, optional
            Name of the pickle file. The default is the name of the project.
        msg : string, optional
            Log message. The default is "".

        Returns
        -------
        None.

        """
        filename = self.check_name(filename)
        filename = self.dir + "/" + filename.replace(".pickle", "") + ".pickle"
        with open(filename, "wb") as f:
            pickle.dump(data, f)
        self.log("pickle dump to " + filename + (". " + msg if len(msg) else "."))

    def pickle_load(self, filename="__name__", msg=""):
        """
        Parameters
        ----------
        filename : string, optional
            Name of the data file. The default is the name of the project.
        msg : string, optional
            Log message. The default is "".

        Returns
        -------
        data : any
        """
        filename = self.check_name(filename)
        filename = self.dir + "/" + filename.replace(".pickle", "") + ".pickle"
        with open(filename, "rb") as f:
            data = pickle.load(f)
        if len(msg):
            self.log("pickle load from " + filename + ". " + msg)
        else:
            print("pickle load from " + filename + ". ")
        return data

    def plt_save(self, fig, filename="__name__", msg="", **kwargs):
        filename = self.check_name(filename)
        if "." not in filename:
            filename += ".png"
        filename = self.dir + "/" + filename
        fig.savefig(filename, **kwargs)
        self.log("save fig to " + filename + (". " + msg if len(msg) else "."))

    def remove(self):
        shutil.rmtree(self.dir)


if __name__ == "__main__":
    t1 = Project("test", verbose=True, clear=True)
    t1.json_dump({"a": "a"})
    t1.remove()
