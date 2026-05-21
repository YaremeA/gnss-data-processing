import json
import time
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import GNSSMeasurement

@csrf_exempt
def receive_gnss_data(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405
        )
      
    try:
        data = json.loads(request.body)
        measurement = GNSSMeasurement.objects.create(
            local_timestamp=data.get("local_timestamp"),
            unix_timestamp=data.get("unix_timestamp"),
            sentence_type=data.get("sentence_type"),
            raw_nmea=data.get("raw_nmea"),

            fix_status=data.get("fix_status"),
            fix_quality=data.get("fix_quality"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            satellites=data.get("satellites"),
            hdop=data.get("hdop"),
            altitude_m=data.get("altitude_m"),
            speed_kmh=data.get("speed_kmh"),
            course_deg=data.get("course_deg"),
            data_valid=data.get("data_valid"),
            processing_delay_ms=data.get("processing_delay_ms"),
        )
      
        print("Received GNSS data:")
        print(data)
      
        return JsonResponse({
            "status": "ok",
            "message": "GNSS data saved",
            "id": measurement.id,
        })
      
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )
      
def dashboard(request):
    return render(request, "gnss_receiver/dashboard.html")
  
def latest_gnss_data(request):
    measurements = GNSSMeasurement.objects.order_by("-created_at")[:50]
    measurements = list(reversed(measurements))
    latest_position = (
        GNSSMeasurement.objects
        .exclude(latitude__isnull=True)
        .exclude(longitude__isnull=True)
        .order_by("-created_at")
        .first()
    )
    latest_gga = (
        GNSSMeasurement.objects
        .filter(sentence_type="GGA")
        .order_by("-created_at")
        .first()
    )
    data = []
  
    for item in measurements:
        data.append({
            "id": item.id,
            "local_timestamp": item.local_timestamp,
            "sentence_type": item.sentence_type,
            "raw_nmea": item.raw_nmea,
            "fix_status": item.fix_status,
            "fix_quality": item.fix_quality,
            "latitude": item.latitude,
            "longitude": item.longitude,
            "satellites": item.satellites,
            "hdop": item.hdop,
            "altitude_m": item.altitude_m,
            "speed_kmh": item.speed_kmh,
            "course_deg": item.course_deg,
            "data_valid": item.data_valid,
            "processing_delay_ms": item.processing_delay_ms,
        })
      
    summary = {
        "latitude": latest_position.latitude if latest_position else None,
        "longitude": latest_position.longitude if latest_position else None,
        "speed_kmh": latest_position.speed_kmh if latest_position else None,
        "raw_nmea": latest_position.raw_nmea if latest_position else None,
        "local_timestamp": latest_position.local_timestamp if latest_position else None,
        "fix_status": latest_gga.fix_status if latest_gga else None,
        "fix_quality": latest_gga.fix_quality if latest_gga else None,
        "satellites": latest_gga.satellites if latest_gga else None,
        "hdop": latest_gga.hdop if latest_gga else None,
        "altitude_m": latest_gga.altitude_m if latest_gga else None,
        "sentence_type": latest_position.sentence_type if latest_position else None,
        "processing_delay_ms": measurements[-1].processing_delay_ms if measurements else None,
    }
    return JsonResponse({
        "data": data,
        "summary": summary,
    })
  
import time
@csrf_exempt
def latency_test(request):
    start_time = time.perf_counter()
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    content_type = request.content_type
    if content_type == "application/json":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except:
            data = {}
    elif content_type == "text/plain":
        data = request.body.decode("utf-8")
    elif content_type == "application/x-www-form-urlencoded":
        data = request.POST.dict()
    elif content_type.startswith("multipart/form-data"):
        data = request.POST.dict()
    else:
        data = request.body.decode("utf-8")
    end_time = time.perf_counter()
    return JsonResponse({
        "status": "ok",
        "content_type": content_type,
        "server_processing_time_ms": (end_time - start_time) * 1000
    })
