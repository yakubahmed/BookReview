import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('postgres://jbgzwaswtepkqo:31b250316c82f24ff2508f0d20d5c23c985af44d5e2beebaf7c0eec0f1626bc3@ec2-174-129-255-91.compute-1.amazonaws.com:5432/d40tr17b3mpcf1')
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader)
    for isbn,title,author,year in reader:
        db.execute("INSERT INTO book (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year+'-12-31'})
        print(f"Added book with isbn {isbn}.")
    db.commit()

if __name__ == "__main__":
    main()
