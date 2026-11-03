package local.sc51g;

import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.Matrix;
import android.graphics.Rect;
import android.graphics.RectF;
import android.graphics.drawable.Drawable;
import android.media.AudioAttributes;
import android.media.SoundPool;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.Switch;
import android.widget.TextView;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.WeakHashMap;

/** App-local sound controls. Does not change device volume or system settings. */
public final class ShutterSoundControl {
    private static final String TAG = "sc51g_shutter_sound";
    private static final String PREFS = "sc51g_port_sound";
    private static SoundPool pool;
    private static final Map<String, Integer> samples = new HashMap<>();
    private static final Set<Integer> loaded = new HashSet<>();
    private static final Set<Integer> pending = new HashSet<>();
    private static Context application;
    private static final Map<View, Boolean> toolbarAdjusted = new WeakHashMap<>();

    private static SharedPreferences prefs(Context context) {
        return context.getApplicationContext().getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    public static boolean isEnabled(Context context) {
        return prefs(context).getBoolean("enabled", true);
    }

    private static int volume(Context context) {
        return Math.max(1, Math.min(100, prefs(context).getInt("volume", 50)));
    }

    private static int dp(Context context, int value) {
        return Math.round(value * context.getResources().getDisplayMetrics().density);
    }

    public static void addToList(ViewGroup group, List<View> buttons) {
        View existing = group.findViewWithTag(TAG);
        if (existing == null) {
            final ImageView button = new ImageView(group.getContext());
            button.setTag(TAG);
            button.setId(View.generateViewId());
            button.setScaleType(ImageView.ScaleType.CENTER);
            int background = group.getResources().getIdentifier("primary_shortcut_selector", "drawable", group.getContext().getPackageName());
            if (background != 0) button.setBackgroundResource(background);
            int sizeId = group.getResources().getIdentifier("left_icon_area_height", "dimen", group.getContext().getPackageName());
            int size = sizeId == 0 ? dp(group.getContext(), 48) : group.getResources().getDimensionPixelSize(sizeId);
            group.addView(button, new FrameLayout.LayoutParams(size, size));
            button.setOnClickListener(view -> showDialog(button));
            refresh(button);
            existing = button;
            preload(group.getContext());
        }
        if (!buttons.isEmpty() && buttons.get(buttons.size()-1)!=null) {
            existing.setRotation(buttons.get(buttons.size()-1).getRotation());
        }
        // Place next to the timer and flash in the existing shortcut layout.
        buttons.add(Math.max(0, buttons.size() - 2), existing);
        group.post(() -> fitToolbarBelowInsets(group));
    }

    private static void fitToolbarBelowInsets(ViewGroup group) {
        // Xperia's rotated HUD assumes a screen origin at (0,0). One UI keeps a
        // cutout inset, which clips most of the original shortcut row.
        if (!(group.getParent() instanceof View) || group.getWidth() == 0) return;
        View toolbar = (View) group.getParent();
        if (!(toolbar.getParent() instanceof View)) return;
        if (toolbarAdjusted.containsKey(toolbar)) return;
        // The SC-51G uses the portrait window with the legacy landscape HUD
        // rotated inside it. Its top row needs the window's cutout offset.
        int inset = 0;
        WindowInsets insets = group.getRootWindowInsets();
        if (insets != null) inset = insets.getInsetsIgnoringVisibility(
                WindowInsets.Type.statusBars() | WindowInsets.Type.displayCutout()).top;
        int statusHeight = group.getResources().getIdentifier("status_bar_height", "dimen", "android");
        if (statusHeight != 0) inset = Math.max(inset, group.getResources().getDimensionPixelSize(statusHeight));
        if (inset == 0) return;
        Matrix parent = new Matrix();
        ((View) toolbar.getParent()).transformMatrixToGlobal(parent);
        Matrix inverse = new Matrix();
        if (!parent.invert(inverse)) return;
        float[] shift = {0, inset};
        inverse.mapVectors(shift);
        toolbarAdjusted.put(toolbar, true);
        Log.i("SC51GUI", "toolbar inset=" + inset + " shift=" + shift[0] + "," + shift[1]);
        toolbar.setTranslationX(toolbar.getTranslationX() + shift[0]);
        toolbar.setTranslationY(toolbar.getTranslationY() + shift[1]);
        toolbar.setBackgroundColor(0x99000000);
    }

    public static void rotate(ViewGroup group, float angle) {
        View button = group.findViewWithTag(TAG);
        if (button != null) button.setRotation(angle);
    }

    private static void refresh(ImageView button) {
        boolean enabled = isEnabled(button.getContext());
        int volume = volume(button.getContext());
        String description = enabled ? "シャッター音：有効・音量 " + volume + "%" : "シャッター音：消音";
        button.setContentDescription(description);
        button.setTooltipText(description);
        button.setImageDrawable(new SpeakerIcon(button.getContext(), enabled));
    }

    private static void showDialog(final ImageView button) {
        final Context context = button.getContext();
        LinearLayout content = new LinearLayout(context);
        content.setOrientation(LinearLayout.VERTICAL);
        int margin = dp(context, 24);
        content.setPadding(margin, dp(context, 8), margin, dp(context, 8));
        final Switch enabled = new Switch(context);
        enabled.setText("シャッター音を鳴らす");
        enabled.setChecked(isEnabled(context));
        enabled.setMinHeight(dp(context, 48));
        content.addView(enabled, new LinearLayout.LayoutParams(-1, -2));
        final TextView label = new TextView(context);
        label.setText("音量 " + volume(context) + "%");
        label.setPadding(0, dp(context, 18), 0, dp(context, 8));
        content.addView(label);
        final SeekBar slider = new SeekBar(context);
        slider.setContentDescription("シャッター音の音量");
        slider.setMax(99);
        slider.setProgress(volume(context) - 1);
        slider.setEnabled(enabled.isChecked());
        content.addView(slider, new LinearLayout.LayoutParams(-1, dp(context, 48)));
        final Button preview = new Button(context);
        preview.setText("音を確認");
        preview.setEnabled(enabled.isChecked());
        preview.setOnClickListener(view -> playShutter(context, "SHUTTER_CLICK"));
        content.addView(preview);
        TextView note = new TextView(context);
        note.setText("端末のメディア音量に合わせて再生します。");
        note.setTextSize(12);
        note.setPadding(0, dp(context, 8), 0, 0);
        content.addView(note);
        enabled.setOnCheckedChangeListener((view, checked) -> {
            prefs(context).edit().putBoolean("enabled", checked).apply();
            slider.setEnabled(checked);
            preview.setEnabled(checked);
            refresh(button);
            Log.i("SC51GSound", "enabled=" + checked + " volume=" + volume(context));
        });
        slider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar bar, int progress, boolean user) {
                int value = progress + 1;
                label.setText("音量 " + value + "%");
                if (user) {
                    prefs(context).edit().putInt("volume", value).apply();
                    refresh(button);
                }
            }
            @Override public void onStartTrackingTouch(SeekBar bar) {}
            @Override public void onStopTrackingTouch(SeekBar bar) {
                Log.i("SC51GSound", "volume=" + volume(context));
            }
        });
        new AlertDialog.Builder(context).setTitle("シャッター音").setView(content).setPositiveButton("閉じる", null).show();
    }

    private static synchronized void preload(Context context) {
        if (pool != null) return;
        application = context.getApplicationContext();
        pool = new SoundPool.Builder().setMaxStreams(2).setAudioAttributes(
                new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_MEDIA)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build()).build();
        pool.setOnLoadCompleteListener((soundPool, sample, status) -> {
            synchronized (ShutterSoundControl.class) {
                if (status == 0) {
                    loaded.add(sample);
                    if (pending.remove(sample)) playSample(sample);
                } else {
                    pending.remove(sample);
                    Log.w("SC51GSound", "sample load failed: " + status);
                }
            }
        });
        String[] types = {"SHUTTER_CLICK", "SHUTTER_CLICK_FIRST_HALF", "SHUTTER_CLICK_SECOND_HALF"};
        String[] names = {"camera_click", "camera_click_first_half", "camera_click_second_half"};
        for (int i = 0; i < types.length; i++) {
            int resource = application.getResources().getIdentifier(names[i], "raw", application.getPackageName());
            if (resource != 0) samples.put(types[i], pool.load(application, resource, 1));
        }
    }

    /** Returns true for shutter sounds, leaving video start/stop sounds to the original app. */
    public static synchronized boolean playShutter(Context context, String type) {
        if (type == null || !type.startsWith("SHUTTER_CLICK")) return false;
        preload(context);
        if (!isEnabled(context)) {
            Log.i("SC51GSound", "shutter muted");
            return true;
        }
        Integer sample = samples.get(type);
        if (sample == null || sample <= 0) {
            Log.w("SC51GSound", "shutter sample missing: " + type);
        } else if (loaded.contains(sample)) {
            playSample(sample);
        } else {
            pending.add(sample);
        }
        return true;
    }

    private static void playSample(int sample) {
        if (!isEnabled(application)) return;
        float gain = volume(application) / 100f;
        int stream = pool.play(sample, gain, gain, 1, 0, 1f);
        Log.i("SC51GSound", "shutter gain=" + gain + " stream=" + stream);
    }

    private static final class SpeakerIcon extends Drawable {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        private final boolean enabled;
        private final int size;
        SpeakerIcon(Context context, boolean enabled) { this.enabled = enabled; size = dp(context, 24); }
        @Override public int getIntrinsicWidth() { return size; }
        @Override public int getIntrinsicHeight() { return size; }
        @Override public void draw(Canvas canvas) {
            canvas.save();
            canvas.translate(getBounds().left, getBounds().top);
            canvas.scale(getBounds().width() / 24f, getBounds().height() / 24f);
            paint.setColor(enabled ? Color.WHITE : 0xffffd54f);
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(1.7f);
            paint.setStrokeCap(Paint.Cap.ROUND);
            paint.setStrokeJoin(Paint.Join.ROUND);
            Path speaker = new Path();
            speaker.moveTo(3, 9); speaker.lineTo(7, 9); speaker.lineTo(12, 5);
            speaker.lineTo(12, 19); speaker.lineTo(7, 15); speaker.lineTo(3, 15); speaker.close();
            canvas.drawPath(speaker, paint);
            if (enabled) {
                canvas.drawArc(new RectF(10, 5, 22, 19), -55, 110, false, paint);
                canvas.drawArc(new RectF(11, 8, 17, 16), -55, 110, false, paint);
            } else {
                canvas.drawLine(16, 9, 21, 15, paint); canvas.drawLine(21, 9, 16, 15, paint);
            }
            canvas.restore();
        }
        @Override public void setAlpha(int alpha) { paint.setAlpha(alpha); invalidateSelf(); }
        @Override public void setColorFilter(android.graphics.ColorFilter filter) { paint.setColorFilter(filter); invalidateSelf(); }
        @Override public int getOpacity() { return android.graphics.PixelFormat.TRANSLUCENT; }
    }
}
