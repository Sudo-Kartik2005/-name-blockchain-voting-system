#!/usr/bin/env python3
from app import app
from models import Voter

def main():
    with app.app_context():
        admins = Voter.query.filter_by(is_admin=True).all()
        print('ADMINS:', [(a.username, a.email, a.is_admin) for a in admins])

if __name__ == '__main__':
    main()


