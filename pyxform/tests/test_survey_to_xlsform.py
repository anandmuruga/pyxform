'''
.. module:: test_survey_to_xlsform
    :Date: 2014/09/16
    
.. codeauthor:: Esmail Fadae <esmail.fadae@kobotoolbox.org>
'''


import unittest
import os.path
import tempfile

import pyxform.survey_from

from pyxform import constants


class Test_SurveyToXlsForm(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        
        # Record the path to all files in the 'example_xml' directory.    
        test_directory_path= os.path.dirname(__file__)
        self.xform_directory_path= os.path.join(test_directory_path, 'example_xforms')
        
        self.xform_in_paths= [ os.path.join(self.xform_directory_path, filename) \
                        for filename in os.listdir(self.xform_directory_path)]


    def test_consistent_export(self):
        '''
        Test that exporting a form to CSV and XLS result in the same data.
        '''
                
        for xform_in_p in self.xform_in_paths:            
            # Import and store the XForm.
            xform_survey= pyxform.survey_from.xform(xform_in_p)
            
            with tempfile.NamedTemporaryFile(suffix='-pyxform.xls') as xls_tempfile:
                # Export the XForm survey to an XLS-formatted XLSForm file.
                xform_survey.to_xls(xls_tempfile.name)
                # Import the XLSForm back in.
                xls_survey= pyxform.survey_from.xls(xls_tempfile)

            with tempfile.NamedTemporaryFile(suffix='-pyxform.csv') as csv_tempfile:
                # Export the XForm survey to a CSV-formatted XLSForm file.
                xform_survey.to_csv(csv_tempfile.name)
                # Import the XLSForm back in.
                csv_survey= pyxform.survey_from.csv(csv_tempfile)

            self.assertEqual(xls_survey, csv_survey, 'XLS and CSV XLSForm mismatch for "{}".'.format(xform_in_p))


    def test_unicode(self):
        '''
        Test that Unicode text is correctly exported and re-importable.
        '''
        
        EXPECTED_QUESTION_LABEL= u"Don't you just \u2764 Unicode\u203d"
        XML_SURVEY_FILENAME= 'unicode_survey.xml'
        
        # Get the Unicode survey's absolute path.
        unicode_survey_path= [xform_in_p for xform_in_p in self.xform_in_paths \
                             if os.path.split(xform_in_p)[1] == XML_SURVEY_FILENAME ][0]
        
        xform_survey= pyxform.survey_from.xform(unicode_survey_path)
        
        # Test XLS re-import.
        with tempfile.NamedTemporaryFile(suffix='-pyxform.xls') as xls_tempfile:
            xform_survey.to_xls(xls_tempfile.name)
            xls_survey= pyxform.survey_from.xls(xls_tempfile)
        
            xls_question_label= xls_survey[constants.CHILDREN][0][constants.LABEL]
            self.assertEqual(xls_question_label, EXPECTED_QUESTION_LABEL)
        

    def test_all_question_types_kf2(self):
        '''
        Test that all question types generated by KoBoForm 2 can be exported 
        and re-imported correctly.
        '''
        
        from pyxform.aliases import get_xform_question_type # Used by this test only (currently)

        expected_child_info= \
          [(u'Select_One_question', u'select one'),
           (u'Select_Many_question', u'select all that apply'),
           (u'Text_question', u'text'),
           (u'Number_question', u'integer'),
           (u'Decimal_question', u'decimal'),
           (u'Date_question', u'date'),
           (u'Time_question', u'time'),
           (u'Date__Time_question', u'dateTime'),
           (u'GPS_question', u'geopoint'),
           (u'Photo_question', u'image'),
           (u'Audio_question', u'audio'),
           (u'Video_question', u'video'),
           (u'Barcode_question', u'barcode'),
           (u'Acknowledge_question', u'acknowledge'),
           (u'start', u'start'),
           (u'end', u'end'),
           (u'deviceid', u'deviceid'),
           (u'meta', u'group')]

        # Import the XForm then export it to XLS and re-import the XLSForm.
        xform_survey= pyxform.survey_from.xform(os.path.join(self.xform_directory_path, 'all_question_types_survey_kf2.xml'))
        with tempfile.NamedTemporaryFile(suffix='-pyxform.xls') as xls_tempfile:
            xform_survey.to_xls(xls_tempfile.name)
            xls_survey= pyxform.survey_from.xls(xls_tempfile)

        for i, (xform_child, xls_child) in enumerate( zip(xform_survey['children'], xls_survey['children']) ):
            expected_name, expected_type=  expected_child_info[i]
            
            self.assertEqual(xform_child['name'], expected_name)
            self.assertEqual(xls_child['name'], expected_name)
            
            # Check that the types from the imports all de-alias to the same thing as the expected types.
            self.assertEqual(get_xform_question_type(xform_child['type']), get_xform_question_type(expected_type))
            self.assertEqual(get_xform_question_type(xls_child['type']), get_xform_question_type(expected_type))
            

    def test_question_types_imported_in_order_kf1(self):
        '''
        tests the order and types match the expected output for a KoBoForm 1 
        XForm.
        '''
        
        expected_qtypes_list = \
          [(u'deviceid', u'deviceid'),
          (u'start', u'start'),
          (u'end', u'end'),
          (u'Select_One_question', u'select one'),
          (u'Select_Many_question', u'select all that apply'),
          (u'Text_question', u'string'),
          (u'Number_question', u'int'),
          (u'Decimal_question', u'decimal'),
          (u'Date_question', u'date'),
          (u'Time_question', u'time'),
          (u'Date__Time_question', u'dateTime'),
          (u'GPS_question', u'geopoint'),
          (u'Photo_question', u'image'),
          (u'Audio_question', u'audio'),
          (u'Video_question', u'video'),
          (u'Barcode_question', u'barcode'),
          (u'Acknowledge_question', u'acknowledge')]
        
        survey = pyxform.survey_from.xform(os.path.join(self.xform_directory_path, 'all_question_types_survey_kf1.xml'))
        question_types_list = list()
        for q in survey['children']:
            question_types_list.append( (q['name'], q['type']) )
        self.assertListEqual(question_types_list, expected_qtypes_list)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()