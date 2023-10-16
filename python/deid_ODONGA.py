import re
import sys

            
def check_for_age(patient, note, chunk, output_handle):
    """
    Inputs:
        - patient: Patient Number, will be printed in each occurance of personal information found
        - note: Note Number, will be printed in each occurance of personal information found
        - chunk: one whole record of a patient
        - output_handle: an opened file handle. The results will be written to this file.
            to avoid the time intensive operation of opening and closing the file multiple times
            during the de-identification process, the file is opened beforehand and the handle is passed
            to this function.
    Logic:
        Search the entire chunk for phone number occurances. Find the location of these occurances
        relative to the start of the chunk, and output these to the output_handle file.
        If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
        Use the precompiled regular expression to find phones.

        1. Search the entire chunk for occurances of age in the text
        2. Check if the age values are greater than 89 as per HIPAA regulations.
        3. Find the location of these occurances relative to the start of the chunk, and output these to the output_handle file.
        4. If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
    """
    # The perl code handles texts a bit differently,
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write("Patient {}\tNote {}\n".format(patient, note))

    # Patterns of age regular expression
    age_pattern = ["\d{2,}yo|\d{2,} yo|\d{2,} yr old|\d{2,} year old|\d{2,} years old"]

    for age_pat in age_pattern:
        matches = re.finditer(age_pat, chunk, flags=re.IGNORECASE)

        for match in matches:
            identified_age_match = match.group()
            age_value = int(identified_age_match[:2])   # Get only the first two values
            # Check if the identified age variable is greater than 89 as per HIPAA definitions
            if age_value > 89:
                result = (
                    str(match.start() - offset)
                    + " "
                    + str(match.start() - offset)
                    + " "
                    + str(match.end() - offset)
                )
                output_handle.write(result + "\n")

def deid_age(text_path= 'id.text', output_path = 'age.phi'):
    """
    Inputs: 
        - text_path: path to the file containing patient records
        - output_path: path to the output file.
    
    Outputs:
        for each patient note, the output file will start by a line declaring the note in the format of:
            Patient X Note Y
        then for each phone number found, it will have another line in the format of:
            start start end
        where the start is the start position of the detected phone number string, and end is the detected
        end position of the string both relative to the start of the patient note.
        If there is no phone number detected in the patient note, only the first line (Patient X Note Y) is printed
        to the output
    Screen Display:
        For each phone number detected, the following information will be displayed on the screen for debugging purposes 
        (these will not be written to the output file):
            start end phone_number
        where `start` is the start position of the detected phone number string, and `end` is the detected end position of the string
        both relative to the start of patient note.
    """
    # start of each note has the patter: START_OF_RECORD=PATIENT||||NOTE||||
    # where PATIENT is the patient number and NOTE is the note number.
    start_of_record_pattern = '^start_of_record=(\d+)\|\|\|\|(\d+)\|\|\|\|$'

    # end of each note has the patter: ||||END_OF_RECORD
    end_of_record_pattern = '\|\|\|\|END_OF_RECORD$'

    # open the output file just once to save time on the time intensive IO
    with open(output_path,'w+') as output_file:
        with open(text_path) as text:
            # initilize an empty chunk. Go through the input file line by line
            # whenever we see the start_of_record pattern, note patient and note numbers and start 
            # adding everything to the 'chunk' until we see the end_of_record.
            chunk = ''
            for line in text:
                record_start = re.findall(start_of_record_pattern,line,flags=re.IGNORECASE)
                if len(record_start):
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line,flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
                    check_for_age(patient,note,chunk.strip(), output_file)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''
                
if __name__== "__main__":
    # deid_phone(sys.argv[1], sys.argv[2])
    deid_age(sys.argv[1], sys.argv[2])
    