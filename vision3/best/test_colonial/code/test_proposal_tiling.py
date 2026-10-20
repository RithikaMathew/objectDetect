import unittest
import numpy as np
from PIL import Image
from proposal_tiling import origins,tiled_proposals


class TilingTests(unittest.TestCase):
    def test_edge_coverage(self):
        for length in (300,480,720,960):
            covered=np.zeros(length,bool)
            for x in origins(length,320,.25):covered[x:min(x+320,length)]=True
            self.assertTrue(covered.all())

    def test_offsets_and_class_aware_duplicate_merging(self):
        # 640px image, two non-overlapping tiles; full frame and right tile
        # describe the same person. Different-class overlapping bike survives.
        def infer(image):
            if image.width==640:
                return dict(boxes=np.array([[330,10,350,40],[330,10,350,40]]),scores=[.9,.8],text_labels=['person','bicycle'])
            return dict(boxes=np.array([[10,10,30,40]]),scores=[.7],text_labels=['person'])
        r=tiled_proposals(Image.new('RGB',(640,200)),infer,size=320,overlap=0)
        self.assertEqual(r['text_labels'],['person','bicycle','person'])
        np.testing.assert_array_equal(r['boxes'],[[330,10,350,40],[330,10,350,40],[10,10,30,40]])

    def test_empty_outputs(self):
        def infer(image):return dict(boxes=[],scores=[],text_labels=[])
        r=tiled_proposals(Image.new('RGB',(720,480)),infer)
        self.assertEqual(r['boxes'].shape,(0,4))


if __name__=='__main__':unittest.main()
