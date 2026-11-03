.class public final Llocal/sc51g/GalaxyCamera;
.super Ljava/lang/Object;

.method public static get(Landroid/hardware/camera2/CaptureRequest;Landroid/hardware/camera2/CaptureRequest$Key;)Ljava/lang/Object;
    .locals 1
    :try_start
    invoke-virtual {p0, p1}, Landroid/hardware/camera2/CaptureRequest;->get(Landroid/hardware/camera2/CaptureRequest$Key;)Ljava/lang/Object;
    move-result-object v0
    return-object v0
    :try_end
    .catch Ljava/lang/IllegalArgumentException; {:try_start .. :try_end} :unsupported
    :unsupported
    move-exception v0
    const/4 v0, 0x0
    return-object v0
.end method

.method public static set(Landroid/hardware/camera2/CaptureRequest$Builder;Landroid/hardware/camera2/CaptureRequest$Key;Ljava/lang/Object;)V
    .locals 2
    invoke-virtual {p1}, Landroid/hardware/camera2/CaptureRequest$Key;->getName()Ljava/lang/String;
    move-result-object v0
    const-string v1, "android."
    invoke-virtual {v0, v1}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :done
    :try_start
    invoke-virtual {p0, p1, p2}, Landroid/hardware/camera2/CaptureRequest$Builder;->set(Landroid/hardware/camera2/CaptureRequest$Key;Ljava/lang/Object;)V
    :try_end
    .catch Ljava/lang/IllegalArgumentException; {:try_start .. :try_end} :unsupported
    goto :done
    :unsupported
    move-exception v0
    const-string v0, "SC51GPort"
    invoke-virtual {p1}, Landroid/hardware/camera2/CaptureRequest$Key;->getName()Ljava/lang/String;
    move-result-object v1
    invoke-static {v0, v1}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I
    :done
    return-void
.end method
