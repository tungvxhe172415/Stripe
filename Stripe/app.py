from flask import Flask, render_template, url_for, request, abort, jsonify

import stripe
import json
import os
app = Flask(__name__)

app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51Pdl3rJHbjFDVzJgSnx1vgAhDpHRwg0bvxADlGWVp1hgAfUhtBr9WHvUcOtkvccwwe7zvRcQsw5EH2Dsj6z1PQD100sSri9LN6'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51Pdl3rJHbjFDVzJgt095OKZve22d79CS5wd21eWMod0jeNvAV5tQoVnY7qX5jb3BbYGDzN7xPkA7ZGsdiYwqk1Nq006E5hRJrn'

# app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51PdkJHC50r8w1WypFckYO40ufNnO8OAx3fpNquCGGY7V1RhlX3jhxchE3bqLQI6WBHcb885uTOYwFQDPzw1xjaDR00oIdIYEe1'
# app.config['STRIPE_SECRET_KEY'] = 'sk_test_51PdkJHC50r8w1Wyp29t231TiZbKDcIVZlS0FEPPLiVP8gICZxBBIeXRSSYcvKMdtMihSdlVzfClkBlA6BHlujTC200uXBzjknw'


stripe.api_key = app.config['STRIPE_SECRET_KEY']

@app.route('/')
def index():
    '''
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1GtKWtIdX0gthvYPm4fJgrOr',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    '''
    return render_template(
        'index.html', 
        #checkout_session_id=session['id'], 
        #checkout_public_key=app.config['STRIPE_PUBLIC_KEY']
    )
products = [
        {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Sản phẩm 1',
                    'description': 'Mô tả sản phẩm 1',
                },
                'unit_amount': 2000,
            },
            'quantity': 1,
        },
        {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Sản phẩm 2',
                    'description': 'Mô tả sản phẩm 2',
                },
                'unit_amount': 3000,
            },
            'quantity': 1,
        },
        {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Sản phẩm 3',
                    'description': 'Mô tả sản phẩm 3',
                },
                'unit_amount': 1500,
            },
            'quantity': 2,
        },
    ]


@app.route('/stripe_pay')
def stripe_pay():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        # line_items=[{
        #     'price': 'price_1PdpSaC50r8w1WypVaxuB7Cz',
        #     'quantity': 1,
        # }]
        line_items=products
        ,
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'], 
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'whsec_134ff31d098af893ac7486a59be5a9d6fdff7eeedaf2593655aff044623d59db'
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('INVALID SIGNATURE')
        return {}, 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items['data'][0]['description'])

    return {}



endpoint_secret = 'whsec_134ff31d098af893ac7486a59be5a9d6fdff7eeedaf2593655aff044623d59db'


@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
      payment_intent = event['data']['object']
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)



















if __name__ == '__main__':
    app.run(debug=True)