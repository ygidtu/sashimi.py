#!/usr/bin/env python3
# -*- coding:utf-8 -*-
u"""
Created at 2022.03.22 by ygidtu@gmail.com

This is used to create heatmap images for multiple signal files contains in bigWig file
"""
import os

import numpy as np

from sashimi.base.GenomicLoci import GenomicLoci
from sashimi.base.ReadDepth import ReadDepth
from sashimi.base.Readder import Reader
from sashimi.file.File import File


class Bigwig(File):

    def __init__(self, path: str, label: str = "", title: str = ""):
        u"""
        :param path: the path to bam file
        :param label: the left axis label
        """
        super().__init__(path)
        self.label = label
        self.title = title

    @classmethod
    def create(cls, path: str, label: str = "", title: str = ""):
        assert os.path.exists(path), f"{path} is not exists."
        if not label:
            label = os.path.basename(path)
        return cls(path=path, label=label, title=title)

    def load(self, region: GenomicLoci, **kwargs):
        self.region = region
        self.data = ReadDepth(np.nan_to_num(
            Reader.read_bigwig(self.path, region),
            copy=True, nan=0.0, posinf=None, neginf=None
        ))


if __name__ == "__main__":
    bw = Bigwig.create("../../example/bws/1.bw")
    bw.load(GenomicLoci("chr1", 1270656, 1284730, "+"))

    print(bw.data.wiggle)
    print(max(bw.data.wiggle), min(bw.data.wiggle))
    print(bw.data.junctions_dict)
    print(bw.data.plus)
    print(bw.data.minus)
    pass
