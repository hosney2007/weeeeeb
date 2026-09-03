from models.booking import Booking
from models.branch import Branch
from models.course import Course
from models.schedaule import Schedule


def _make_schedule(db_session):
    course = Course(
        title="Math 101",
        description="Intro to math",
        course_type="offline",
        is_active=True,
    )
    branch = Branch(name="Main Branch")
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
    return course, branch, schedule


def _booking_payload(course, branch, schedule, **overrides):
    data = {
        "student_name": "Sara Ali",
        "student_number": "01000000000",
        "parent_number": "01111111111",
        "grade": "Grade 1",
        "mode": "offline",
        "addational_notes": "no notes",
        "exam": str(course.id),
        "branch_id": str(branch.id),
        "schedule_id": str(schedule.id),
    }
    data.update(overrides)
    return data


class TestBooking:
    def test_creates_a_booking(self, client, db_session):
        course, branch, schedule = _make_schedule(db_session)

        resp = client.post(
            "/booking", data=_booking_payload(course, branch, schedule)
        )
        assert resp.status_code == 302

        bookings = Booking.query.all()
        assert len(bookings) == 1
        assert bookings[0].student_number == "01000000000"
        assert bookings[0].status == "pending"

    def test_blocks_duplicate_booking_same_phone_same_group(self, client, db_session):
        course, branch, schedule = _make_schedule(db_session)
        payload = _booking_payload(course, branch, schedule)

        client.post("/booking", data=payload)
        client.post("/booking", data=payload)  # same phone, same schedule again

        bookings = Booking.query.all()
        assert len(bookings) == 1

    def test_allows_same_phone_in_a_different_group(self, client, db_session):
        course, branch, schedule = _make_schedule(db_session)
        other_schedule = Schedule(
            course_id=course.id,
            branch_id=branch.id,
            day1="Monday",
            day2="Wednesday",
            time1="14:00",
            time2="16:00",
            level="beginner",
            mode="offline",
        )
        db_session.add(other_schedule)
        db_session.commit()

        payload = _booking_payload(course, branch, schedule)
        client.post("/booking", data=payload)

        payload2 = _booking_payload(course, branch, other_schedule)
        client.post("/booking", data=payload2)

        assert Booking.query.count() == 2

    def test_booking_links_to_logged_in_user(self, client, db_session, make_user, login):
        course, branch, schedule = _make_schedule(db_session)
        user = make_user(email="parent@example.com", password="password123")
        login("parent@example.com", "password123")

        client.post("/booking", data=_booking_payload(course, branch, schedule))

        booking = Booking.query.first()
        assert booking.user_id == user.id
