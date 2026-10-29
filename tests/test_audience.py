"""Unit tests for target tenant audience classification and filtering."""

import pytest
from src.classification.audience import (
    TargetAudience,
    detect_target_audience,
    get_audience_label_uz,
    get_audience_icon,
)


def test_detect_family_uzbek():
    assert detect_target_audience("Chilonzor 9", "Faqat oilaga beriladi, zags bilan") == "family"
    assert detect_target_audience("3 xonali uy yosh oilaga", "Toza va tartibli saqlaydigan oilaga") == "family"
    assert detect_target_audience("Novostroyka Qorasaroy", "oilaga arenda kvartira zaks qog'ozi bilan") == "family"


def test_detect_family_russian():
    assert detect_target_audience("Аренда квартиры", "Сдается только семейным парам без животных") == "family"
    assert detect_target_audience("Квартира для семьи", "Официальный брак, загс обязателен") == "family"
    assert detect_target_audience("3 комнатная", "Семья молодожёны либо иностранцы") == "family"


def test_detect_female_uzbek():
    assert detect_target_audience("Qizlarga kvartira", "Talaba qizlar uchun joy bor Chilonzor") == "female"
    assert detect_target_audience("Sheriklikka qiz olamiz", "Ishlaydigan yoki oqiydigan qiz bolaga") == "female"
    assert detect_target_audience("Koyko joy", "Faqat ayollar uchun shinam xona") == "female"


def test_detect_female_russian():
    assert detect_target_audience("Сдам комнату женщине или девушке", "В квартире все условия для девушек") == "female"
    assert detect_target_audience("Аренда", "Только студенткам или порядочным женщинам") == "female"


def test_detect_male_uzbek():
    assert detect_target_audience("Talaba yigitlar uchun kvartira", "Yangi ToshMI yaqinida yigitlarga") == "male"
    assert detect_target_audience("O'g'il bola sherik olamiz", "Bollarga kvartira Yunusobodda") == "male"
    assert detect_target_audience("Угил боларга квартира бор", "киши бошига 800 минг") == "male"


def test_detect_male_russian():
    assert detect_target_audience("Койко место для мальчиков", "Только работающим парням и мужчинам") == "male"
    assert detect_target_audience("Квартира для парней", "Студентам парням сдается") == "male"


def test_negations_handled_properly():
    # When listing says "students / boys NOT accepted"
    res = detect_target_audience("Сдается 2 ком Чиланзар", "Студентам не сдается. Только семье.")
    assert res == "family"

    res_no_students = detect_target_audience("3 xonali kvartira", "Bolalarga berilmaydi. Faqat oilaga.")
    assert res_no_students == "family"


def test_unrestricted_defaults_to_any():
    assert detect_target_audience("2 xonali kvartira Chilonzor", "Evro remont, hamma texnika bor.") == "any"
    assert detect_target_audience("Yunusobod 4-mavze", "Uzoq muddatga beriladi.") == "any"


def test_helper_labels_and_icons():
    assert get_audience_label_uz("family") == "Oila uchun"
    assert get_audience_label_uz("female") == "Qizlar uchun"
    assert get_audience_label_uz("male") == "Yigitlar uchun"
    assert get_audience_label_uz("any") == "Barchaga"

    assert get_audience_icon("family") == "👨‍👩‍👧"
    assert get_audience_icon("female") == "👩"
    assert get_audience_icon("male") == "👨"
    assert get_audience_icon("any") == "👥"

