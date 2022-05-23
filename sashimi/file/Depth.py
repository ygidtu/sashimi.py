#!/usr/bin/env python3
# -*- coding:utf-8 -*-
u"""
This file contains the object to handle depth file generated using samtools depth.
"""
import gzip
import os
from typing import List, Optional

import numpy as np

from sashimi.base.GenomicLoci import GenomicLoci
from sashimi.base.ReadDepth import ReadDepth
from sashimi.base.Readder import Reader
from sashimi.file.File import File


class Depth(File):
    u"""
    To generate depth file from bams
    1. samtools depth *.bam | bgzip > depth.bgz
    2. tabix -s 2 -e 2 depth.bgz
    """

    def __init__(self, path: str, label: List[str] = None, title: str = ""):
        super().__init__(path)
        self.label = label
        self.title = title
        self.region = None

    def __len__(self) -> int:
        return len(self.data)

    @classmethod
    def create(cls, path: str, label: List[str] = None, title: str = ""):
        u"""
        create depth obj
        """
        assert os.path.exists(path), f"{path} not exists."

        with gzip.open(path, "rt") as r:
            for line in r:
                lines = line.split()

                if label:
                    assert len(lines) - 2 == len(label), \
                        f"the number of columns [{len(lines) - 2}] must equal to the number of labels [{len(label)}]"
                else:
                    label = list(range(1, len(lines) - 1))
                break

        return cls(path, label, title)

    def load(self, region: GenomicLoci, required_sample: List[str] = None, log_trans: Optional[str] = None):
        u"""
        depth file generated by samtools depth

        samtools depth *.bam | bgzip > depth.gz && tabix indexed tabix -s 1 -b 2 -e 3 depth.gz
        :param region: the region to query
        :param required_sample: the sample to use
        :param log_trans: log transform
        :return:
        """
        self.region = region
        self.log_trans = log_trans
        if not required_sample:
            required_sample = self.label

        required_sample = [x for x in required_sample if x in self.label]
        depth_vector = {x: np.zeros(len(region), dtype='f') for x in required_sample}

        for row in Reader.read_depth(self.path, region):
            chrom, site = row[0], int(row[1]) - region.start

            if site < len(region):
                vals = {x: float(y) for x, y in zip(self.label, row[2:])}
                for x in depth_vector.keys():
                    depth_vector[x] += vals[x]

        self.data = {x: ReadDepth(y) for x, y in depth_vector.items()}

    def items(self):
        if self.data:
            for x, y in self.data.items():
                yield x, y


if __name__ == '__main__':
    depth = Depth.create("../../example/depth.bgz")
    region = GenomicLoci(chromosome="chr1", start=1017198, end=1051741, strand="-")

    depth.load(region)

    for k, v in depth.data.items():
        print(k, v)
