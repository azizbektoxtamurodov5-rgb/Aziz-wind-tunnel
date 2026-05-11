[app]
title = Aziz Wind Tunnel
package.name = azizwindtunnel
package.domain = com.aziz.windtunnel

source.dir = .
source.include_exts = py,png,jpg,mp3,wav,ogg,ttf,atlas
source.include_patterns = *.mp3,*.wav

source.main = main.py
version = 1.0

# pygame + numpy (p4a da ishlaydi, opencv kerak emas)
requirements = pygame

# p4a develop branch — barqaror va to'liq

android.permissions = CAMERA,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21

# 25b — buildozer tavsiya etgan versiya
android.ndk = 21e
android.ndk_api = 21

android.accept_sdk_license = True

# Faqat ARM64 (tezroq)
android.archs = arm64-v8a

android.orientation = landscape
android.fullscreen = 1
android.features = android.hardware.camera, android.hardware.camera.autofocus
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
