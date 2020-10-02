import io
import argparse
import sys
from PIL import Image
from google.cloud import vision
'''
Please note, that to use vision API you need to 
download credentials key, and put its localisation under the environmental
variable GOOGLE_APPLICATION_CREDENTIALS.
More details here:
https://cloud.google.com/vision/docs/quickstart-client-libraries
'''

PELLET_LIST = [
    'AK 30', 'AM 2', 'AMC 30', 'AMP 10', 'AMP 2', 'ATM 30', 'AUG 30',
    'AX 20', 'C 30', 'CAZ 10', 'CD 2', 'CFM 5', 'CFR 30', 'CIP 5',
    'CN 10', 'CN 30', 'CN 500', 'CRO 30', 'CT 50', 'CTX 5', 'E 15',
    'ERY 15', 'ETP 10', 'FC 10', 'F 100', 'FEC 40', 'FEP 30', 'FF 200',
    'FOX 30', 'IMI 10', 'IPM 10', 'L 15', 'LEV 5', 'LNZ 10', 'LVX 5',
    'MEC 10', 'MEM 10', 'MRP 10', 'MXF 5', 'NA 30', 'NET 10', 'NOR 10',
    'OX 1', 'P 1', 'PRL 30', 'PT 15', 'RA 5', 'RD 5', 'S 300',
    'SXT 25', 'TC 75', 'TEC 30', 'TEM 30', 'TET 30', 'TGC 15', 'TIC 75',
    'TIM 85', 'TOB 10', 'TPZ 36', 'TTC 85', 'TZP 36', 'VA 30', 'VA 5']


def match_exact(recognised):
    pellet_list_no_spaces = [pel.replace(' ', '') for pel in PELLET_LIST]
    recognised = recognised.upper()
    if recognised in pellet_list_no_spaces:
        return PELLET_LIST[pellet_list_no_spaces.index(recognised)]
    else:
        return None

def match_exact_2(letters, numbers):
    for pel in PELLET_LIST:
        pel_let, pel_num = pel.split()
        if letters.upper() == pel_let and numbers == pel_num:
            return pel
    return None

# TODO implement partial way of matching antibiotic labels
def match_partial(letters, numbers):
    for pel in PELLET_LIST:
        pel_let, pel_num = pel.split()
        if letters.upper() == pel_let and numbers == pel_num:
            return pel
    return None

def filter_letters_and_numbers(text):
    return ''.join([c for c in text if c.isalpha() or c.isdigit()])

def get_content(image):
    byte_io = io.BytesIO()
    image.save(byte_io, format='PNG')
    return byte_io.getvalue()

def detect_text(image_pil):
    client = vision.ImageAnnotatorClient(client_options={})

    image = vision.types.Image(content=get_content(image_pil))

    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    texts = response.text_annotations

    dig_list = []
    let_list = []

    for text in texts:
        letters = ''.join([c for c in text.description if c.isalpha()])
        digits = ''.join([c for c in text.description if c.isdigit()])
        if letters:
            let_list.append(letters)
        if digits:
            dig_list.append(digits)

    for let in let_list:
        for dig in dig_list:
            rec = match_exact_2(let, dig)
            if rec:
                return rec

    return None

def detect_antibiotic(path):
    image_pil = Image.open(path, 'r')
    for angle in range(0, 360, 20):
        detected = detect_text(image_pil.rotate(angle))
        if detected:
            return detected.replace(' ', '')
    return None

def test_batch(annotation_path):
    cnt_good = 0
    cnt_bad = 0
    cnt_nothing = 0
    with open(annotation_path, 'r') as an_file:
        for idx, line in enumerate(an_file):
            line = line.rstrip('\n')
            path, label = line.split(' ')
            detected = detect_antibiotic(path)
            print("{}. ".format(idx + 1), end='')
            if detected is None:
                cnt_nothing += 1
                print("Not recognised {} {}".format(path, label))
            elif detected != label:
                cnt_bad += 1
                print("Recognised incorrectly {} {}".format(path, label))
            else:
                cnt_good += 1
                print("OK")

    print("Recognised correctly {}".format(cnt_good))
    print("Recognised incorrectly {}".format(cnt_bad))
    print("Not recognised {}".format(cnt_nothing))

def main():
    parser = argparse.ArgumentParser(description='Test how well OCR recognition works.')
    parser.add_argument('--batch_test', help='', required=False)
    parser.add_argument('--detect', help='', required=False)
    args = parser.parse_args()

    if args.detect is None and args.batch_test is None:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if args.detect:
        print("Detected antibiotic {}".format(detect_antibiotic(args.detect)))
    if args.batch_test:
        print("Entering batch test mode...")
        test_batch(args.batch_test)


if __name__ == '__main__':
    main()
