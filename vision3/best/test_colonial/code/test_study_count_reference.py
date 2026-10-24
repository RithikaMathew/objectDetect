import datetime as dt
import unittest
from study_count_reference import extract

class ManualReferenceTests(unittest.TestCase):
    def table(self):
        return {'Bicycles':[['Start Date','08/28/2019'],['Channel','NB Bike Lane','SB Sidewalk'],['Direction','Northbound','Southbound'],['11:45 PM','2','3','999'],['12:00 AM','4','','999']]}

    def test_day_rollover_and_derived_total_exclusion(self):
        rows,coverage=extract(self.table())
        self.assertEqual(len(rows),4)
        self.assertEqual(rows[2]['bin_start'],'2019-08-29 00:00:00')
        self.assertEqual(sum(r['count']for r in rows if r['status']=='recorded'),9)
        self.assertEqual({r['camera_side_label']for r in rows},{'NB','SB'})

    def test_missing_count_is_not_zero(self):
        rows,_=extract(self.table())
        self.assertEqual(rows[-1]['status'],'missing');self.assertEqual(rows[-1]['count'],'')
        self.assertFalse(any(r['user_type']=='pedestrian'for r in rows))

    def test_interval_end_exclusive(self):
        rows,_=extract(self.table(),dt.datetime(2019,8,28,23,45),dt.datetime(2019,8,29))
        self.assertEqual(len(rows),2);self.assertTrue(all(r['bin_start']=='2019-08-28 23:45:00'for r in rows))

    def test_invalid_counts_are_not_silently_coerced(self):
        data=self.table();data['Bicycles'][-1][1]='2.5'
        with self.assertRaises(ValueError):extract(data)

if __name__=='__main__':unittest.main()
