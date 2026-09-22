import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import app
from utils.db import get_db_connection

def test_app():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()

    conn = get_db_connection()
    admin_user = conn.execute("SELECT username FROM users WHERE is_admin = 1").fetchone()
    student_user = conn.execute("SELECT username FROM users WHERE is_admin = 0 LIMIT 1").fetchone()
    conn.close()

    print(f"Testing with admin: {admin_user['username'] if admin_user else 'None'}")
    print(f"Testing with student: {student_user['username'] if student_user else 'None'}")

    # 1. Test Admin Dashboard
    with client.session_transaction() as sess:
        sess['admin'] = True
        sess['admin_user'] = admin_user['username'] if admin_user else 'admin'

    res = client.get('/admin')
    assert res.status_code == 200, f"Admin status {res.status_code}"
    assert b"Arrears" in res.data, "Arrears not found in admin HTML"
    assert b"Total Failed Subjects" in res.data, "Total system arrears card not found"
    print("✓ Admin dashboard test passed")

    # 2. Test Admin User View
    if student_user:
        res = client.get(f"/admin/user/{student_user['username']}")
        assert res.status_code == 200, f"Admin user status {res.status_code}"
        assert b"Arrears" in res.data, "Arrears not found in student details HTML"
        assert b"A+ Grades" in res.data, "A+ Grades not found in student details HTML"
        assert b"A Grades" in res.data, "A Grades not found in student details HTML"
        print("✓ Admin user details test passed")

    # 3. Test Student Dashboard
    with client.session_transaction() as sess:
        sess.clear()
        sess['user'] = student_user['username'] if student_user else 'student'

    res = client.get('/dashboard')
    assert res.status_code == 200, f"Dashboard status {res.status_code}"
    assert b"Arrears" in res.data, "Arrears not found in dashboard HTML"
    assert b"A+ Grades" in res.data, "A+ Grades not found in dashboard HTML"
    assert b"A Grades" in res.data, "A Grades not found in dashboard HTML"
    print("✓ Student dashboard test passed")

    # 4. Test Student Profile
    res = client.get('/profile')
    assert res.status_code == 200, f"Profile status {res.status_code}"
    assert b"Academic Summary" in res.data, "Academic summary not found in profile HTML"
    assert b"Arrears" in res.data, "Arrears not found in profile HTML"
    assert b"A+ Grades" in res.data, "A+ Grades not found in profile HTML"
    assert b"A Grades" in res.data, "A Grades not found in profile HTML"
    print("✓ Student profile test passed")

    print("\nALL ROUTE VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_app()
