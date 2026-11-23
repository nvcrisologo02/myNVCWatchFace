package com.nvc.fakeglucose;

import android.content.BroadcastReceiver;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.util.Log;

import androidx.wear.watchface.complications.datasource.ComplicationDataSourceUpdateRequester;

/**
 * Sets the fake state and pushes it to every slot showing a fake provider. Extras (all optional,
 * missing ones keep their previous value): value (int mg/dL), age_min (int), trend (string),
 * empty (boolean, glucose has no data), age_empty (boolean, age has no data).
 */
public class SetStateReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        SharedPreferences.Editor e = FakeState.prefs(context).edit();
        if (intent.hasExtra("value")) e.putInt("value", intent.getIntExtra("value", 112));
        if (intent.hasExtra("age_min")) e.putInt("age_min", intent.getIntExtra("age_min", 4));
        if (intent.hasExtra("trend")) e.putString("trend", intent.getStringExtra("trend"));
        e.putBoolean("empty", intent.getBooleanExtra("empty", false));
        e.putBoolean("age_empty", intent.getBooleanExtra("age_empty", false));
        e.commit();

        for (Class<?> c : new Class<?>[]{FakeRangeService.class, FakeTextService.class, FakeAgeService.class}) {
            ComplicationDataSourceUpdateRequester
                    .create(context, new ComponentName(context, c))
                    .requestUpdateAll();
        }
        Log.i(FakeServiceBase.TAG, "state set: " + FakeState.prefs(context).getAll());
    }
}
