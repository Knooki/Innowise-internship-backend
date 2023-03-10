import datetime

from rest_framework import serializers


class BlockPageSerializer(serializers.Serializer):
    blocktime_in_days = serializers.IntegerField(min_value=0, default=0)
    blocktime_in_hours = serializers.IntegerField(min_value=0, default=0)
    blocktime_in_minutes = serializers.IntegerField(min_value=0, default=0)
    is_permanent_blocked = serializers.BooleanField(default=False)

    def validate(self, data):
        block_days = data.get("blocktime_in_days")
        block_hours = data.get("blocktime_in_hours")
        block_minutes = data.get("blocktime_in_minutes")
        is_permanent = data.get("is_permanent_blocked")

        if is_permanent:
            data["unblock_date"] = None
            return data

        data.clear()
        data["is_permanent_blocked"] = False

        if not any((block_days, block_hours, block_minutes)):
            data["unblock_date"] = None
            return data

        unblock_date = datetime.datetime.now() + datetime.timedelta(
            days=block_days,
            hours=block_hours,
            minutes=block_minutes,
        )
        data["unblock_date"] = unblock_date

        return data

    def update(self, instance, validated_data):
        instance.is_permanent_blocked = validated_data.get("is_permanent_blocked")
        instance.unblock_date = validated_data.get("unblock_date")
        instance.save()
        return instance
