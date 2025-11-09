import json
from datetime import datetime
from functools import lru_cache

from django.conf import settings
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse

from .models import Bike, ContactInquiry, Offer, ServiceBooking, TestRideRequest


def _bike_map():
	"""Return a dictionary mapping bike slugs to bike objects"""
	bikes = Bike.objects.filter(is_active=True)
	return {bike.slug: _bike_to_dict(bike) for bike in bikes}


def _bike_to_dict(bike):
	"""Convert a Bike model instance to a dictionary matching the JSON structure"""
	return {
		'slug': bike.slug,
		'name': bike.name,
		'family': bike.family or '',
		'isFeatured': bike.is_featured,
		'heroImage': bike.hero_image or '',
		'gallery': bike.get_gallery_list(),
		'engine': {
			'cc': float(bike.engine_cc) if bike.engine_cc else 0,
			'ccCategory': bike.cc_category or '',
			'power': bike.power or '',
			'torque': bike.torque or '',
			'cooling': bike.cooling or '',
			'transmission': bike.transmission or '',
		},
		'performance': {
			'mileage': bike.mileage or '',
			'topSpeed': bike.top_speed or '',
			'summary': bike.performance_summary or '',
		},
		'chassis': {
			'frontBrake': bike.front_brake or '',
			'rearBrake': bike.rear_brake or '',
			'suspension': bike.suspension or '',
			'weight': bike.weight or '',
			'seatHeight': bike.seat_height or '',
		},
		'colors': bike.get_colors_list(),
		'price': {
			'exShowroom': float(bike.ex_showroom_price) if bike.ex_showroom_price else 0,
			'onRoad': float(bike.on_road_price) if bike.on_road_price else 0,
			'emi': bike.emi or '',
		},
		'features': bike.get_features_list(),
	}


def _bike_choices():
	"""Return a list of bike choices for forms"""
	bikes = Bike.objects.filter(is_active=True).order_by('name')
	return [{'slug': bike.slug, 'name': bike.name} for bike in bikes]


def _base_context():
	return {
		'static_prefix': static(''),
		'data_url': reverse('bikes_json'),
		'models_root': reverse('models'),
		'detail_pattern': reverse('model_detail', kwargs={'slug': '__slug__'}),
		'book_url': reverse('book_test_ride'),
		'offers_url': reverse('offers'),
		'bike_choices': _bike_choices(),
	}


def bikes_json(request):
	"""API endpoint to return bikes data as JSON (for frontend compatibility)"""
	bikes = Bike.objects.filter(is_active=True)
	bikes_data = [_bike_to_dict(bike) for bike in bikes]
	return JsonResponse({'bikes': bikes_data})


def home(request):
	context = _base_context()
	context.update(
		{
			'hero_slides': [
				static('assets/images/one.webp'),
				static('assets/images/six.webp'),
				static('assets/images/eight.avif'),
			]
		}
	)
	return render(request, 'showroom/home.html', context)


def about(request):
	return render(request, 'showroom/about.html', _base_context())


def models_list(request):
	context = _base_context()
	return render(request, 'showroom/models.html', context)


def model_detail(request, slug):
	bike = _bike_map().get(slug)
	if not bike:
		raise Http404('Bike not found')

	context = _base_context()
	context.update(
		{
			'page_slug': slug,
			'selected_bike': bike,
		}
	)
	return render(request, 'showroom/model_detail.html', context)


def offers(request):
	context = _base_context()
	# Get active offers
	from django.utils import timezone
	today = timezone.now().date()
	active_offers = Offer.objects.filter(
		is_active=True,
		valid_from__lte=today,
		valid_until__gte=today
	).select_related('bike')
	context['offers'] = active_offers
	return render(request, 'showroom/offers.html', context)


def book_test_ride(request):
	return render(request, 'showroom/book_test_ride.html', _base_context())


def contact(request):
	return render(request, 'showroom/contact.html', _base_context())


def gallery(request):
	return render(request, 'showroom/gallery.html', _base_context())


def service(request):
	return render(request, 'showroom/service.html', _base_context())


def submit_test_ride(request):
	if request.method != 'POST':
		return redirect('book_test_ride')

	data = request.POST
	bike_slug = data.get('model') or ''
	bike_map = _bike_map()
	if bike_slug not in bike_map:
		messages.error(request, 'Please select a valid bike model.')
		return redirect('book_test_ride')

	try:
		preferred_date = datetime.strptime(data.get('date', ''), '%Y-%m-%d').date()
		preferred_time = datetime.strptime(data.get('time', ''), '%H:%M').time()
	except ValueError:
		messages.error(request, 'Please provide a valid date and time for your test ride request.')
		return redirect('book_test_ride')

	TestRideRequest.objects.create(
		name=data.get('name', '').strip(),
		email=data.get('email', '').strip(),
		phone=data.get('phone', '').strip(),
		bike_slug=bike_slug,
		preferred_date=preferred_date,
		preferred_time=preferred_time,
		notes=data.get('notes', '').strip(),
	)

	messages.success(request, 'Thank you! Our team will call you to confirm your test ride slot shortly.')
	return redirect('book_test_ride')


def submit_contact(request):
	if request.method != 'POST':
		return redirect('contact')

	data = request.POST
	bike_slug = data.get('model', '').strip()
	bike_map = _bike_map()
	if bike_slug and bike_slug not in bike_map:
		messages.error(request, 'Please choose a valid bike model.')
		return redirect('contact')

	ContactInquiry.objects.create(
		name=data.get('name', '').strip(),
		email=data.get('email', '').strip(),
		phone=data.get('phone', '').strip(),
		bike_slug=bike_slug,
		message=data.get('message', '').strip(),
	)

	messages.success(request, 'Thanks for reaching out! Our showroom team will contact you shortly.')
	return redirect('contact')


def submit_service(request):
	if request.method != 'POST':
		return redirect('service')

	data = request.POST
	bike_slug = data.get('model') or ''
	bike_map = _bike_map()
	if bike_slug not in bike_map:
		messages.error(request, 'Please select a valid bike model for the service booking.')
		return redirect('service')

	try:
		preferred_date = datetime.strptime(data.get('date', ''), '%Y-%m-%d').date()
	except ValueError:
		messages.error(request, 'Please choose a valid date for the service visit.')
		return redirect('service')

	ServiceBooking.objects.create(
		name=data.get('name', '').strip(),
		phone=data.get('phone', '').strip(),
		bike_slug=bike_slug,
		preferred_date=preferred_date,
		notes=data.get('notes', '').strip(),
	)

	messages.success(request, 'Service slot request saved. Our advisors will confirm your appointment soon.')
	return redirect('service')
