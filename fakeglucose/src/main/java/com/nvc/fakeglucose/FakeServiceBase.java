package com.nvc.fakeglucose;

import android.os.RemoteException;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.wear.watchface.complications.data.ComplicationData;
import androidx.wear.watchface.complications.data.ComplicationType;
import androidx.wear.watchface.complications.datasource.ComplicationDataSourceService;
import androidx.wear.watchface.complications.datasource.ComplicationRequest;

/** Shared plumbing for the three fake providers. */
abstract class FakeServiceBase extends ComplicationDataSourceService {
    static final String TAG = "FakeGlucose";

    abstract ComplicationData data(FakeState state, ComplicationType type);

    @Override
    public void onComplicationRequest(@NonNull ComplicationRequest request,
                                      @NonNull ComplicationRequestListener listener) {
        ComplicationData d = data(FakeState.load(this), request.getComplicationType());
        Log.i(TAG, getClass().getSimpleName() + " -> " + d);
        try {
            listener.onComplicationData(d);
        } catch (RemoteException e) {
            Log.e(TAG, "could not deliver complication data", e);
        }
    }

    @Nullable
    @Override
    public ComplicationData getPreviewData(@NonNull ComplicationType type) {
        return data(FakeState.load(this), type);
    }
}
