import pytest
from main import shorten_string


def test_shorten_string_no_cut1():
    long_string = "012345678901234567890123456789"
    print(len(long_string))
    max_length = 30
    break_off_right = 2
    expected_output = "012345678901234567890123456789"
    assert shorten_string(long_string, max_length, break_off_right) == expected_output
    assert len(shorten_string(long_string, max_length, break_off_right)) == max_length

def test_shorten_string_no_cut2():
    long_string = "01234"
    max_length = 5
    break_off_right = 2
    expected_output = "01234"
    assert shorten_string(long_string, max_length, break_off_right) == expected_output
    assert len(shorten_string(long_string, max_length, break_off_right)) == max_length

def test_shorten_string_small_cut1():
    long_string = "012345"
    max_length = 5
    break_off_right = 2
    expected_output = "0..45"
    assert shorten_string(long_string, max_length, break_off_right) == expected_output
    assert len(shorten_string(long_string, max_length, break_off_right)) == max_length

def test_shorten_string_small_cut2():
    long_string = "012345"
    max_length = 3
    break_off_right = 1
    expected_output = "012"
    print(shorten_string(long_string, max_length, break_off_right))
    assert shorten_string(long_string, max_length, break_off_right) == expected_output
    assert len(shorten_string(long_string, max_length, break_off_right)) == max_length

def test_shorten_string_small_cut3():
    long_string = "012345"
    max_length = 4
    break_off_right = 1
    expected_output = "0..5"
    print(shorten_string(long_string, max_length, break_off_right))
    assert shorten_string(long_string, max_length, break_off_right) == expected_output
    assert len(shorten_string(long_string, max_length, break_off_right)) == max_length

def test_shorten_string_small_cut4():
    long_string = "012345"
    max_length = 5
    break_off_right = 2
    expected_output = "0..45"
    print(shorten_string(long_string, max_length, break_off_right))
    assert shorten_string(long_string, max_length, break_off_right) == expected_output
    assert len(shorten_string(long_string, max_length, break_off_right)) == max_length

def test_shorten_string_big_cut1():
    # Typical case of a long stringthat needs to be shortened for the screen
    long_string = "01234567890123456789"
    max_length = 15
    break_off_right = 4
    expected_output = "01234567...6789"
    print(shorten_string(long_string, max_length, break_off_right))
    assert shorten_string(long_string, max_length, break_off_right) == expected_output
    assert len(shorten_string(long_string, max_length, break_off_right)) == max_length

def test_shorten_string_big_cut2():
    # Typical case of a long stringthat needs to be shortened for the screen
    long_string = "01234567890123456789"
    max_length = 15
    break_off_right = 12
    expected_output = "0..890123456789"
    print(shorten_string(long_string, max_length, break_off_right))
    assert shorten_string(long_string, max_length, break_off_right) == expected_output
    assert len(shorten_string(long_string, max_length, break_off_right)) == max_length

def test_shorten_string_big_cut3():
    # Typical case of a long stringthat needs to be shortened for the screen
    long_string = "01234567890123456789"
    max_length = 15
    break_off_right = 13
    expected_output = "012345678901234"
    print(shorten_string(long_string, max_length, break_off_right))
    assert shorten_string(long_string, max_length, break_off_right) == expected_output
    assert len(shorten_string(long_string, max_length, break_off_right)) == max_length

def test_shorten_string_bad_input1():
    # Typical case of a long stringthat needs to be shortened for the screen
    long_string = "01234567890123456789"
    max_length = 0
    break_off_right = 13
    expected_output = ""
    print(shorten_string(long_string, max_length, break_off_right))
    assert shorten_string(long_string, max_length, break_off_right) == expected_output
    assert len(shorten_string(long_string, max_length, break_off_right)) == max_length

def test_shorten_string_bad_input2():
    # Typical case of a long stringthat needs to be shortened for the screen
    long_string = ""
    max_length = 4
    break_off_right = 13
    expected_output = ""
    print(shorten_string(long_string, max_length, break_off_right))
    assert shorten_string(long_string, max_length, break_off_right) == expected_output
    assert len(shorten_string(long_string, max_length, break_off_right)) == 0


    
