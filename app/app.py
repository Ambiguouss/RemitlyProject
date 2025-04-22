from flask import Flask, request, jsonify
from models import db, SwiftCode
from setupdb import app




@app.route('/v1/swift-codes/<string:swift_code>', methods=['GET'])
def get_swift_code(swift_code):
    swift_data = SwiftCode.query.filter_by(swift_code=swift_code).first()
    
    if not swift_data:
        return jsonify({"message": "SWIFT code not found"}), 404
    
    response = {
        "address": swift_data.address,
        "bankName": swift_data.bank_name,
        "countryISO2": swift_data.country_iso2,
        "countryName": swift_data.country_name,
        "isHeadquarter": swift_data.is_headquarter,
        "swiftCode": swift_data.swift_code
    }
    
    if swift_data.is_headquarter:
        branches = SwiftCode.query.filter(SwiftCode.swift_code.startswith(swift_code[:8])).all()
        response["branches"] = [
            {
                "address": branch.address,
                "bankName": branch.bank_name,
                "countryISO2": branch.country_iso2,
                "isHeadquarter": branch.is_headquarter,
                "swiftCode": branch.swift_code
            } for branch in branches if branch.swift_code != swift_code
        ]
    
    return jsonify(response)

@app.route('/v1/swift-codes/country/<string:country_iso2>', methods=['GET'])
def get_swift_codes_by_country(country_iso2):
    swift_codes = SwiftCode.query.filter_by(country_iso2=country_iso2.upper()).all()
    
    if not swift_codes:
        return jsonify({"message": "No SWIFT codes found for this country"}), 404
    
    response = {
        "countryISO2": country_iso2.upper(),
        "countryName": swift_codes[0].country_name,
        "swiftCodes": [
            {
                "address": code.address,
                "bankName": code.bank_name,
                "countryISO2": code.country_iso2,
                "isHeadquarter": code.is_headquarter,
                "swiftCode": code.swift_code
            } for code in swift_codes
        ]
    }
    
    return jsonify(response)

@app.route('/v1/swift-codes', methods=['POST'])
def add_swift_code():
    data = request.get_json()
    
    if not data.get('swiftCode') or not data.get('address'):
        return jsonify({"message": "Missing required fields"}), 400
    
    
    new_code = SwiftCode(
        address=data['address'],
        bank_name=data['bankName'],
        country_iso2=data['countryISO2'].upper(),
        country_name=data['countryName'].upper(),
        is_headquarter=data['isHeadquarter'],
        swift_code=data['swiftCode']
    )
    swift_data = SwiftCode.query.filter_by(swift_code=new_code.swift_code).first()
    
    if swift_data:
        return jsonify({"message": "SWIFT code already in the database"}), 400

    db.session.add(new_code)
    db.session.commit()
    
    return jsonify({"message": "SWIFT code added successfully"}), 201

@app.route('/v1/swift-codes/<string:swift_code>', methods=['DELETE'])
def delete_swift_code(swift_code):
    swift_data = SwiftCode.query.filter_by(swift_code=swift_code).first()
    
    if not swift_data:
        return jsonify({"message": "SWIFT code not found"}), 404
    
    db.session.delete(swift_data)
    db.session.commit()
    
    return jsonify({"message": "SWIFT code deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)