import pandas as pd
from models import db, SwiftCode

def parse_swift_data(file_path):
    data = pd.read_csv(file_path)
    
    for _, row in data.iterrows():
        swift_code = row['SWIFT CODE']
        if len(swift_code) == 11:
            existing_code = SwiftCode.query.filter_by(swift_code=swift_code).first()
            if not existing_code:
                new_code = SwiftCode(
                    address=row['ADDRESS'],
                    bank_name=row['NAME'],
                    country_iso2=row['COUNTRY ISO2 CODE'].upper(),
                    country_name=row['COUNTRY NAME'].upper(),
                    is_headquarter=swift_code.endswith('XXX'),
                    swift_code=swift_code
                )
                db.session.add(new_code)
    db.session.commit()
