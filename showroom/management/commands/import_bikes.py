import json
from django.core.management.base import BaseCommand
from showroom.models import Bike


class Command(BaseCommand):
	help = 'Import bikes from bikes.json file into the database'

	def handle(self, *args, **options):
		json_file = 'static/assets/data/bikes.json'
		
		try:
			with open(json_file, 'r', encoding='utf-8') as f:
				data = json.load(f)
			
			bikes_data = data.get('bikes', [])
			created_count = 0
			updated_count = 0
			
			for bike_data in bikes_data:
				slug = bike_data.get('slug')
				if not slug:
					self.stdout.write(self.style.WARNING(f'Skipping bike without slug: {bike_data.get("name")}'))
					continue
				
				bike, created = Bike.objects.update_or_create(
					slug=slug,
					defaults={
						'name': bike_data.get('name', ''),
						'family': bike_data.get('family', ''),
						'is_featured': bike_data.get('isFeatured', False),
						'hero_image': bike_data.get('heroImage', ''),
						'engine_cc': bike_data.get('engine', {}).get('cc', 0),
						'cc_category': bike_data.get('engine', {}).get('ccCategory', ''),
						'power': bike_data.get('engine', {}).get('power', ''),
						'torque': bike_data.get('engine', {}).get('torque', ''),
						'cooling': bike_data.get('engine', {}).get('cooling', ''),
						'transmission': bike_data.get('engine', {}).get('transmission', ''),
						'mileage': bike_data.get('performance', {}).get('mileage', ''),
						'top_speed': bike_data.get('performance', {}).get('topSpeed', ''),
						'performance_summary': bike_data.get('performance', {}).get('summary', ''),
						'front_brake': bike_data.get('chassis', {}).get('frontBrake', ''),
						'rear_brake': bike_data.get('chassis', {}).get('rearBrake', ''),
						'suspension': bike_data.get('chassis', {}).get('suspension', ''),
						'weight': bike_data.get('chassis', {}).get('weight', ''),
						'seat_height': bike_data.get('chassis', {}).get('seatHeight', ''),
						'colors': ', '.join(bike_data.get('colors', [])),
						'ex_showroom_price': bike_data.get('price', {}).get('exShowroom', 0),
						'on_road_price': bike_data.get('price', {}).get('onRoad', 0),
						'emi': bike_data.get('price', {}).get('emi', ''),
						'features': ', '.join(bike_data.get('features', [])),
						'gallery_images': ', '.join(bike_data.get('gallery', [])),
						'is_active': True,
					}
				)
				
				if created:
					created_count += 1
					self.stdout.write(self.style.SUCCESS(f'Created: {bike.name}'))
				else:
					updated_count += 1
					self.stdout.write(self.style.SUCCESS(f'Updated: {bike.name}'))
			
			self.stdout.write(self.style.SUCCESS(
				f'\nImport complete! Created: {created_count}, Updated: {updated_count}'
			))
			
		except FileNotFoundError:
			self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
		except json.JSONDecodeError as e:
			self.stdout.write(self.style.ERROR(f'Error parsing JSON: {e}'))
		except Exception as e:
			self.stdout.write(self.style.ERROR(f'Error: {e}'))

