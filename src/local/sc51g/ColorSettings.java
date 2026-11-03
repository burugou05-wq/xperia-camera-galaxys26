package local.sc51g;

import android.app.AlertDialog;
import android.content.Context;
import android.graphics.Color;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.Switch;
import android.widget.TextView;
import java.util.List;

public final class ColorSettings {
    private static final String TAG="sc51g_color_settings",PREFS="sc51g_port_color";
    public static boolean enabled(Context c) { return c.getSharedPreferences(PREFS,0).getBoolean("enabled",false); }
    public static int strength(Context c) { return Math.max(0,Math.min(100,c.getSharedPreferences(PREFS,0).getInt("strength",35))); }
    private static int dp(Context c,int n) { return Math.round(c.getResources().getDisplayMetrics().density*n); }
    public static void addToList(ViewGroup group,List<View> list) {
        View existing=group.findViewWithTag(TAG);
        if (existing==null) {
            TextView button=new TextView(group.getContext()); button.setTag(TAG);
            button.setText("色"); button.setTextSize(18); button.setGravity(Gravity.CENTER);
            button.setTextColor(Color.WHITE); button.setContentDescription("色の処理");
            int background=group.getResources().getIdentifier("primary_shortcut_selector","drawable",group.getContext().getPackageName());
            if (background!=0) button.setBackgroundResource(background);
            int dimen=group.getResources().getIdentifier("left_icon_area_height","dimen",group.getContext().getPackageName());
            int size=dimen==0?dp(group.getContext(),48):group.getResources().getDimensionPixelSize(dimen);
            group.addView(button,new FrameLayout.LayoutParams(size,size));
            button.setOnClickListener(v->show(button));
            existing=button; refresh(button);
        }
        if (!list.isEmpty() && list.get(list.size()-1)!=null) existing.setRotation(list.get(list.size()-1).getRotation());
        list.add(Math.max(0,list.size()-2),existing);
    }
    public static void rotate(ViewGroup group,float angle) { View v=group.findViewWithTag(TAG); if(v!=null)v.setRotation(angle); }
    private static void refresh(TextView button) {
        button.setTextColor(enabled(button.getContext())?0xffffd54f:Color.WHITE);
        button.setContentDescription("色の処理："+(enabled(button.getContext())?"Web比較補正 "+strength(button.getContext())+"%":"標準"));
    }
    private static void show(TextView button) {
        Context c=button.getContext(); LinearLayout content=new LinearLayout(c); content.setOrientation(1);
        int pad=dp(c,24); content.setPadding(pad,dp(c,8),pad,dp(c,8));
        Switch active=new Switch(c); active.setText("Web比較補正（実験）"); active.setChecked(enabled(c)); active.setMinHeight(dp(c,48)); content.addView(active);
        TextView label=new TextView(c); label.setText("強さ "+strength(c)+"%"); label.setPadding(0,dp(c,12),0,0);content.addView(label);
        SeekBar amount=new SeekBar(c);amount.setMax(100);amount.setProgress(strength(c));amount.setContentDescription("Web比較補正の強さ");amount.setEnabled(active.isChecked());
        content.addView(amount,new LinearLayout.LayoutParams(-1,dp(c,48)));
        TextView note=new TextView(c); note.setText("保存する写真だけに反映します。プレビューと動画は変わりません。\n\nXperia 1 VIIとGalaxy S26の公開カラーチャートを参考にした補正です。Sony純正の画作りを再現するものではありません。\n\n暖色・寒色は、既存の「色合い・明るさ」から調整できます。");note.setTextSize(13);content.addView(note);
        active.setOnCheckedChangeListener((v,on)->{c.getSharedPreferences(PREFS,0).edit().putBoolean("enabled",on).apply();amount.setEnabled(on);refresh(button);});
        amount.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar b,int n,boolean user){label.setText("強さ "+n+"%");if(user){c.getSharedPreferences(PREFS,0).edit().putInt("strength",n).apply();refresh(button);}}
            public void onStartTrackingTouch(SeekBar b){} public void onStopTrackingTouch(SeekBar b){}
        });
        new AlertDialog.Builder(c).setTitle("色の処理").setView(content).setPositiveButton("閉じる",null).show();
    }
}
