import pytest
from sqlalchemy.exc import IntegrityError

from models.branch import Branch
from models.course import Course
from models.schedaule import Schedule
from models.booking import Booking


def test_booking_relationships_resolve(db_session):
    course = Course(title="Physics", description="d", course_type="offline")
    branch = Branch(name="Downtown")
    db_session.add_all([course, branch])
    db_session.commit()

    schedule = Schedule(
        course_id=course.id,
        branch_id=branch.id,
        day1="Sunday",
        day2="Tuesday",
        time1="10:00",
        time2="12:00",
        level="beginner",
        mode="offline",
    )
    db_session.add(schedule)
    db_session.commit()

    booking = Booking(
        student_name="Omar",
        student_number="0100",
        parent_number="0111",
        grade="Grade 2",
        addational_notes="-",
        course_id=course.id,
        schedule_id=schedule.id,
        branch_id=branch.id,
        mode="offline",
    )
    db_session.add(booking)
    db_session.commit()

    # Relationships should resolve both ways.
    assert booking.course.title == "Physics"
    assert booking.schedule.branch.name == "Downtown"
    assert booking in schedule.bookings


def test_branch_name_must_be_unique(db_session):
    db_session.add(Branch(name="Downtown"))
    db_session.commit()

    db_session.add(Branch(name="Downtown"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_booking_requires_a_schedule(db_session):
    course = Course(title="Physics", description="d", course_type="offline")
    db_session.add(course)
    db_session.commit()

    booking = Booking(
        student_name="Omar",
        student_number="0100",
        parent_number="0111",
        grade="Grade 2",
        addational_notes="-",
        course_id=course.id,
        schedule_id=None,
        mode="offline",
    )
    db_session.add(booking)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
