package com.nvc.fakeglucose;

import androidx.wear.watchface.complications.data.ComplicationData;
import androidx.wear.watchface.complications.data.ComplicationType;

public class FakeRangeService extends FakeServiceBase {
    @Override
    ComplicationData data(FakeState state, ComplicationType type) {
        return state.range(type);
    }
}
