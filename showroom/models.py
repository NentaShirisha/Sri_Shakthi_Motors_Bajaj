from django.db import models
from django.core.validators import MinValueValidator


class Bike(models.Model):
	# Essential fields only
	slug = models.SlugField(max_length=100, unique=True)
	name = models.CharField(max_length=200)
	family = models.CharField(max_length=100, blank=True, default='')
	is_featured = models.BooleanField(default=False)
	hero_image = models.CharField(max_length=200, blank=True, help_text="Path to hero image (e.g., assets/images/one.webp)")
	
	# Engine specifications (all optional)
	engine_cc = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
	cc_category = models.CharField(max_length=50, blank=True, default='')
	power = models.CharField(max_length=100, blank=True, default='')
	torque = models.CharField(max_length=100, blank=True, default='')
	cooling = models.CharField(max_length=100, blank=True, default='')
	transmission = models.CharField(max_length=100, blank=True, default='')
	
	# Performance (all optional)
	mileage = models.CharField(max_length=100, blank=True, default='')
	top_speed = models.CharField(max_length=100, blank=True, default='')
	performance_summary = models.TextField(blank=True, default='')
	
	# Chassis (all optional)
	front_brake = models.CharField(max_length=200, blank=True, default='')
	rear_brake = models.CharField(max_length=200, blank=True, default='')
	suspension = models.CharField(max_length=200, blank=True, default='')
	weight = models.CharField(max_length=50, blank=True, default='')
	seat_height = models.CharField(max_length=50, blank=True, default='')
	
	# Colors (optional)
	colors = models.TextField(blank=True, default='', help_text="Enter colors separated by commas")
	
	# Pricing (essential)
	ex_showroom_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
	on_road_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
	emi = models.CharField(max_length=100, blank=True, default='', help_text="e.g., ₹3,599/month")
	
	# Features (optional)
	features = models.TextField(blank=True, default='', help_text="Enter features separated by commas or newlines")
	
	# Gallery images (optional)
	gallery_images = models.TextField(blank=True, default='', help_text="Enter image paths separated by commas")
	
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['-is_featured', 'name']
		verbose_name = 'Bike'
		verbose_name_plural = 'Bikes'
	
	def __str__(self):
		return self.name
	
	def get_colors_list(self):
		"""Return colors as a list"""
		if not self.colors:
			return []
		return [color.strip() for color in self.colors.split(',') if color.strip()]
	
	def get_features_list(self):
		"""Return features as a list"""
		if not self.features:
			return []
		features = self.features.replace('\n', ',').split(',')
		return [feature.strip() for feature in features if feature.strip()]
	
	def get_gallery_list(self):
		"""Return gallery images as a list"""
		if not self.gallery_images:
			return []
		return [img.strip() for img in self.gallery_images.split(',') if img.strip()]


class Offer(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField()
	bike = models.ForeignKey(Bike, on_delete=models.CASCADE, null=True, blank=True, 
	                        help_text="Leave blank for general offers")
	discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
	                                         validators=[MinValueValidator(0)], 
	                                         help_text="Discount percentage (e.g., 10.00 for 10%)")
	discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
	                                     validators=[MinValueValidator(0)],
	                                     help_text="Discount amount in rupees")
	valid_from = models.DateField()
	valid_until = models.DateField()
	is_active = models.BooleanField(default=True)
	image = models.CharField(max_length=200, blank=True, 
	                        help_text="Path to offer image (optional)")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		ordering = ['-is_active', '-valid_from']
		verbose_name = 'Offer'
		verbose_name_plural = 'Offers'
	
	def __str__(self):
		bike_name = f" - {self.bike.name}" if self.bike else ""
		return f"{self.title}{bike_name}"


class TestRideRequest(models.Model):
	name = models.CharField(max_length=120)
	email = models.EmailField()
	phone = models.CharField(max_length=20)
	bike_slug = models.CharField(max_length=80)
	preferred_date = models.DateField()
	preferred_time = models.TimeField()
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Test Ride: {self.name} - {self.bike_slug}"


class ContactInquiry(models.Model):
	name = models.CharField(max_length=120)
	email = models.EmailField()
	phone = models.CharField(max_length=20)
	bike_slug = models.CharField(max_length=80, blank=True)
	message = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Inquiry: {self.name}"


class ServiceBooking(models.Model):
	name = models.CharField(max_length=120)
	phone = models.CharField(max_length=20)
	bike_slug = models.CharField(max_length=80)
	preferred_date = models.DateField()
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Service: {self.name} - {self.bike_slug}"
