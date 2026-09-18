'use client';

import { useEffect, useRef } from 'react';
import * as BABYLON from '@babylonjs/core';
import * as GUI from '@babylonjs/gui';

export default function BabylonScene() {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        if (!canvasRef.current) return;

        const canvas = canvasRef.current;
        const engine = new BABYLON.Engine(canvas, true);

        const createScene = () => {
            const scene = new BABYLON.Scene(engine);
            scene.clearColor = new BABYLON.Color4(0.02, 0.05, 0.1, 1); // Obsidian

            // 1. COLD PALETTE LIGHTING (Obsidian, Chrome, Dodger Blue)
            const hdrTexture = BABYLON.CubeTexture.CreateFromPrefilteredData(
                "https://assets.babylonjs.com/environments/environmentSpecular.env",
                scene
            );
            scene.environmentTexture = hdrTexture;

            // Cold blue light for that 'SLA113' ambient feel
            const light = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(0, 1, 0), scene);
            light.diffuse = new BABYLON.Color3(0.5, 0.7, 1); // Cold Dodger Blue
            light.intensity = 0.8;

            // 2. INDUSTRIAL FOUNDRY TEXTURES (PBR) - Chrome/Steel
            const metalMat = new BABYLON.PBRMaterial("foundryMetal", scene);
            metalMat.metallic = 1.0;
            metalMat.roughness = 0.15;
            metalMat.albedoColor = new BABYLON.Color3(0.15, 0.18, 0.22); // Steel Gray

            const chromeMat = new BABYLON.PBRMaterial("chrome", scene);
            chromeMat.metallic = 1.0;
            chromeMat.roughness = 0.05;
            chromeMat.albedoColor = new BABYLON.Color3(0.8, 0.85, 0.9); // Chrome

            const foundryFloor = BABYLON.MeshBuilder.CreateGround("floor", {width: 20, height: 20}, scene);
            foundryFloor.material = metalMat;

            // Grid lines
            const gridMat = new BABYLON.StandardMaterial("grid", scene);
            gridMat.emissiveColor = new BABYLON.Color3(0.1, 0.3, 0.6); // Dodger Blue
            gridMat.alpha = 0.3;

            for (let i = -10; i <= 10; i++) {
                const lineX = BABYLON.MeshBuilder.CreateLines("lineX" + i, {
                    points: [new BABYLON.Vector3(i, 0.01, -10), new BABYLON.Vector3(i, 0.01, 10)]
                }, scene);
                lineX.color = new BABYLON.Color3(0.1, 0.4, 0.8);
                lineX.alpha = 0.2;

                const lineZ = BABYLON.MeshBuilder.CreateLines("lineZ" + i, {
                    points: [new BABYLON.Vector3(-10, 0.01, i), new BABYLON.Vector3(10, 0.01, i)]
                }, scene);
                lineZ.color = new BABYLON.Color3(0.1, 0.4, 0.8);
                lineZ.alpha = 0.2;
            }

            // 3. THE HUD (Obsidian Cold)
            const advancedTexture = GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI");

            // Top left - SLA113
            const slaText = new GUI.TextBlock();
            slaText.text = "SLA113 // OPERATOR";
            slaText.color = "#1E90FF"; // Dodger Blue
            slaText.fontSize = 18;
            slaText.fontFamily = "monospace";
            slaText.textHorizontalAlignment = GUI.Control.HORIZONTAL_ALIGNMENT_LEFT;
            slaText.left = "20px";
            slaText.top = "-45%";
            advancedTexture.addControl(slaText);

            // Top right - Latency (positioned with left to avoid TypeScript error)
            const latencyText = new GUI.TextBlock();
            latencyText.text = "⚡ 65ms | ONLINE";
            latencyText.color = "#1E90FF"; // Dodger Blue
            latencyText.fontSize = 18;
            latencyText.fontFamily = "monospace";
            latencyText.horizontalAlignment = GUI.Control.HORIZONTAL_ALIGNMENT_RIGHT;
            latencyText.top = "-45%";
            latencyText.paddingRight = "20px";
            advancedTexture.addControl(latencyText);

            // Bottom - System info
            const sysText = new GUI.TextBlock();
            sysText.text = "SLA113_OS_V7.4.2 // COLD_INFRASTRUCTURE";
            sysText.color = "#4A4F57"; // Steel Gray
            sysText.fontSize = 12;
            sysText.fontFamily = "monospace";
            sysText.textHorizontalAlignment = GUI.Control.HORIZONTAL_ALIGNMENT_CENTER;
            sysText.verticalAlignment = GUI.Control.VERTICAL_ALIGNMENT_BOTTOM;
            sysText.paddingBottom = "20px";
            advancedTexture.addControl(sysText);

            // Camera
            const camera = new BABYLON.ArcRotateCamera("camera", Math.PI / 2, Math.PI / 3, 25, BABYLON.Vector3.Zero(), scene);
            camera.attachControl(canvas, true);
            camera.lowerRadiusLimit = 10;
            camera.upperRadiusLimit = 50;

            return scene;
        };

        const scene = createScene();

        engine.runRenderLoop(() => {
            scene.render();
        });

        const handleResize = () => {
            engine.resize();
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            engine.dispose();
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            id="renderCanvas"
            className="w-full h-full touch-none outline-none"
        />
    );
}
