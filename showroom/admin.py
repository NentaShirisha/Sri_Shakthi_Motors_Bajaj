from django.contrib import admin

from .models import Bike, ContactInquiry, Offer, ServiceBooking, TestRideRequest


@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
	list_display = ('name', 'family', 'is_featured', 'is_active', 'ex_showroom_price', 'on_road_price', 'created_at')
	list_filter = ('is_featured', 'is_active', 'family', 'cc_category', 'created_at')
	search_fields = ('name', 'family', 'slug', 'cc_category')
	readonly_fields = ('created_at', 'updated_at')
	
	fieldsets = (
		('Essential Information', {
			'fields': ('name', 'slug', 'family', 'is_featured', 'is_active', 'hero_image'),
			'description': 'Only name is required. Slug will be auto-generated if left empty.'
		}),
		('Pricing', {
			'fields': ('ex_showroom_price', 'on_road_price', 'emi'),
			'description': 'Pricing information (all optional)'
		}),
		('Basic Details', {
			'fields': ('colors', 'features', 'gallery_images'),
			'description': 'Colors, features, and gallery images (all optional)',
			'classes': ('collapse',)
		}),
		('Engine Specifications', {
			'fields': ('engine_cc', 'cc_category', 'power', 'torque', 'cooling', 'transmission'),
			'description': 'Engine details (all optional)',
			'classes': ('collapse',)
		}),
		('Performance', {
			'fields': ('mileage', 'top_speed', 'performance_summary'),
			'description': 'Performance metrics (all optional)',
			'classes': ('collapse',)
		}),
		('Chassis', {
			'fields': ('front_brake', 'rear_brake', 'suspension', 'weight', 'seat_height'),
			'description': 'Chassis and suspension details (all optional)',
			'classes': ('collapse',)
		}),
		('Timestamps', {
			'fields': ('created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)
	
	def save_model(self, request, obj, form, change):
		"""Override save to ensure slug is properly formatted"""
		if not obj.slug:
			from django.utils.text import slugify
			obj.slug = slugify(obj.name)
		super().save_model(request, obj, form, change)


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
	list_display = ('title', 'bike', 'discount_percentage', 'discount_amount', 'valid_from', 'valid_until', 'is_active', 'created_at')
	list_filter = ('is_active', 'valid_from', 'valid_until', 'created_at')
	search_fields = ('title', 'description', 'bike__name')
	readonly_fields = ('created_at', 'updated_at')
	date_hierarchy = 'valid_from'
	
	fieldsets = (
		('Offer Details', {
			'fields': ('title', 'description', 'bike', 'image', 'is_active')
		}),
		('Discount Information', {
			'fields': ('discount_percentage', 'discount_amount'),
			'description': 'Enter either discount percentage or discount amount (or both)'
		}),
		('Validity Period', {
			'fields': ('valid_from', 'valid_until')
		}),
		('Timestamps', {
			'fields': ('created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)


@admin.register(TestRideRequest)
class TestRideRequestAdmin(admin.ModelAdmin):
	list_display = ('name', 'bike_slug', 'preferred_date', 'preferred_time', 'phone', 'email', 'created_at')
	search_fields = ('name', 'phone', 'email', 'bike_slug')
	list_filter = ('preferred_date', 'bike_slug', 'created_at')
	readonly_fields = ('created_at',)
	date_hierarchy = 'preferred_date'


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
	list_display = ('name', 'phone', 'email', 'bike_slug', 'created_at')
	search_fields = ('name', 'phone', 'email', 'bike_slug', 'message')
	list_filter = ('bike_slug', 'created_at')
	readonly_fields = ('created_at',)
	date_hierarchy = 'created_at'


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
	list_display = ('name', 'bike_slug', 'preferred_date', 'phone', 'created_at')
	search_fields = ('name', 'phone', 'bike_slug', 'notes')
	list_filter = ('preferred_date', 'bike_slug', 'created_at')
	readonly_fields = ('created_at',)
	date_hierarchy = 'preferred_date'
