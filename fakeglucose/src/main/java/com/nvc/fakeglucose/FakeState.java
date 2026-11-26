package com.nvc.fakeglucose;

import android.content.Context;
import android.content.SharedPreferences;

import androidx.wear.watchface.complications.data.ComplicationData;
import androidx.wear.watchface.complications.data.ComplicationText;
import androidx.wear.watchface.complications.data.ComplicationType;
import androidx.wear.watchface.complications.data.NoDataComplicationData;
import androidx.wear.watchface.complications.data.PlainComplicationText;
import androidx.wear.watchface.complications.data.RangedValueComplicationData;
import androidx.wear.watchface.complications.data.ShortTextComplicationData;

/** Fake glucose state, set from adb by {@link SetStateReceiver} and read by the services. */
final class FakeState {
    static final float SENSOR_MIN = 20f;   // what Gluroo sends (checked on the watch 2026-11-23)
    static final float SENSOR_MAX = 400f;

    final int value;
    final int ageMinutes;
    final String trend;
    final boolean empty;
    final boolean ageEmpty;

    private FakeState(SharedPreferences p) {
        value = p.getInt("value", 112);
        ageMinutes = p.getInt("age_min", 4);
        trend = p.getString("trend", "→");
        empty = p.getBoolean("empty", false);
        ageEmpty = p.getBoolean("age_empty", false);
    }

    static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences("fake_glucose", Context.MODE_PRIVATE);
    }

    static FakeState load(Context context) {
        return new FakeState(prefs(context));
    }

    private static ComplicationText text(String s) {
        return new PlainComplicationText.Builder(s).build();
    }

    static ComplicationData shortText(String s) {
        return new ShortTextComplicationData.Builder(text(s), text(s)).build();
    }

    ComplicationData range(ComplicationType type) {
        if (empty) {
            return new NoDataComplicationData();
        }
        if (type == ComplicationType.SHORT_TEXT) {
            return shortText(String.valueOf(value));
        }
        float v = Math.max(SENSOR_MIN, Math.min(SENSOR_MAX, value));
        // androidx rejects a ranged value with no text, title or image (the picker then drops the
        // provider: watch, 2026-11-26), so carry the value as text; the faces only read the value.
        return new RangedValueComplicationData.Builder(v, SENSOR_MIN, SENSOR_MAX,
                text(value + " mg/dL")).setText(text(String.valueOf(value))).build();
    }

    ComplicationData glucoseText() {
        return empty ? new NoDataComplicationData() : shortText(value + trend);
    }

    ComplicationData age() {
        return ageEmpty ? new NoDataComplicationData() : shortText(ageMinutes + "m");
    }
}
