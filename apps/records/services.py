from .models import Record, RecordActivityUser
from django.db.models import Count
import boto3
from botocore.exceptions import ClientError
from django.conf import settings

def get_presigned_url(s3_key, expires_in=3600):
    s3 = boto3.client("s3")
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=expires_in
        )
    except ClientError as e:
        print(f"Failed to generate presigned URL: {e}")
        return None
    return url


def get_all_records():
    records = list(Record.objects.all())
    counts_qs = (
        RecordActivityUser.objects.filter(like_status=True)
        .values("record_id")
        .annotate(count=Count("id"))
    )
    counts = {row["record_id"]: row["count"] for row in counts_qs}

    for r in records:
        r.likes_count = counts.get(r.id, 0)
        r.liked_by_user = False
    return records


def create_record(data):
    record = Record.objects.create(**data)
    return record


def get_record_by_id(record_id, user_id=None):
    try:
        record = Record.objects.get(id=record_id)
    except Record.DoesNotExist:
        return None

    count = RecordActivityUser.objects.filter(
        record_id=record_id, like_status=True
    ).count()
    record.likes_count = count

    if user_id is not None:
        exists = RecordActivityUser.objects.filter(
            record_id=record_id, user_id=user_id, like_status=True
        ).exists()
        record.liked_by_user = exists
    else:
        record.liked_by_user = False

    return record


def like_record(user_id, record_id):
    try:
        Record.objects.get(id=record_id)
    except Record.DoesNotExist:
        return None

    RecordActivityUser.objects.update_or_create(
        user_id=user_id,
        record_id=record_id,
        defaults={"like_status": True},
    )

    likes_count = RecordActivityUser.objects.filter(
        record_id=record_id, like_status=True
    ).count()
    return {"likes_count": likes_count, "liked_by_user": True}


def unlike_record(user_id, record_id):
    RecordActivityUser.objects.filter(user_id=user_id, record_id=record_id).delete()
    likes_count = RecordActivityUser.objects.filter(
        record_id=record_id, like_status=True
    ).count()
    return {"likes_count": likes_count, "liked_by_user": False}


def erase_all_records():
    RecordActivityUser.objects.all().delete()
    Record.objects.all().delete()
