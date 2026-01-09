"use client";

import { useRef, useEffect, useCallback } from "react";

interface Ball {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
}

export function GuardrailsAnimation() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const ballRef = useRef<Ball | null>(null);
  const outerFlashRef = useRef<number>(0);
  const animationRef = useRef<number | null>(null);

  const CANVAS_SIZE = 300;
  const OUTER_RADIUS = 140;
  const MIDDLE_RADIUS = 90;
  const BALL_RADIUS = 12;
  const BALL_SPEED = 1.2;

  const initBall = useCallback(() => {
    // Start ball at a random position within the middle circle
    const angle = Math.random() * Math.PI * 2;
    const distance = Math.random() * (MIDDLE_RADIUS - BALL_RADIUS - 10);
    const centerX = CANVAS_SIZE / 2;
    const centerY = CANVAS_SIZE / 2;

    // Random velocity direction
    const velAngle = Math.random() * Math.PI * 2;

    ballRef.current = {
      x: centerX + Math.cos(angle) * distance,
      y: centerY + Math.sin(angle) * distance,
      vx: Math.cos(velAngle) * BALL_SPEED,
      vy: Math.sin(velAngle) * BALL_SPEED,
      radius: BALL_RADIUS,
    };
  }, []);

  const draw = useCallback((ctx: CanvasRenderingContext2D) => {
    const centerX = CANVAS_SIZE / 2;
    const centerY = CANVAS_SIZE / 2;

    // Clear canvas
    ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

    // Draw outer circle (normally invisible, flashes red on collision)
    if (outerFlashRef.current > 0) {
      ctx.beginPath();
      ctx.arc(centerX, centerY, OUTER_RADIUS, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(220, 38, 38, ${outerFlashRef.current * 0.6})`;
      ctx.lineWidth = 3;
      ctx.stroke();

      // Add glow effect
      ctx.shadowColor = `rgba(220, 38, 38, ${outerFlashRef.current * 0.8})`;
      ctx.shadowBlur = 20;
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    // Draw middle circle (always visible, subtle)
    ctx.beginPath();
    ctx.arc(centerX, centerY, MIDDLE_RADIUS, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
    ctx.lineWidth = 1;
    ctx.stroke();

    // Draw ball
    if (ballRef.current) {
      const ball = ballRef.current;
      
      // Ball glow
      ctx.beginPath();
      ctx.arc(ball.x, ball.y, ball.radius + 4, 0, Math.PI * 2);
      const gradient = ctx.createRadialGradient(
        ball.x, ball.y, ball.radius,
        ball.x, ball.y, ball.radius + 8
      );
      gradient.addColorStop(0, "rgba(255, 255, 255, 0.3)");
      gradient.addColorStop(1, "rgba(255, 255, 255, 0)");
      ctx.fillStyle = gradient;
      ctx.fill();

      // Ball body
      ctx.beginPath();
      ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
      ctx.fill();
    }
  }, []);

  const update = useCallback(() => {
    if (!ballRef.current) return;

    const ball = ballRef.current;
    const centerX = CANVAS_SIZE / 2;
    const centerY = CANVAS_SIZE / 2;

    // Update position
    ball.x += ball.vx;
    ball.y += ball.vy;

    // Check collision with outer circle
    const dx = ball.x - centerX;
    const dy = ball.y - centerY;
    const distanceFromCenter = Math.sqrt(dx * dx + dy * dy);

    if (distanceFromCenter + ball.radius >= OUTER_RADIUS) {
      // Collision! Flash the outer circle
      outerFlashRef.current = 1;

      // Calculate reflection
      const normalX = dx / distanceFromCenter;
      const normalY = dy / distanceFromCenter;

      // Reflect velocity
      const dotProduct = ball.vx * normalX + ball.vy * normalY;
      ball.vx = ball.vx - 2 * dotProduct * normalX;
      ball.vy = ball.vy - 2 * dotProduct * normalY;

      // Move ball back inside
      const overlap = distanceFromCenter + ball.radius - OUTER_RADIUS;
      ball.x -= normalX * overlap;
      ball.y -= normalY * overlap;
    }

    // Fade out the flash
    if (outerFlashRef.current > 0) {
      outerFlashRef.current = Math.max(0, outerFlashRef.current - 0.02);
    }
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Handle high DPI displays
    const dpr = window.devicePixelRatio || 1;
    canvas.width = CANVAS_SIZE * dpr;
    canvas.height = CANVAS_SIZE * dpr;
    ctx.scale(dpr, dpr);

    initBall();

    const animate = () => {
      update();
      draw(ctx);
      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [initBall, update, draw]);

  return (
    <canvas
      ref={canvasRef}
      width={CANVAS_SIZE}
      height={CANVAS_SIZE}
      className="opacity-60"
      style={{ width: CANVAS_SIZE, height: CANVAS_SIZE }}
      aria-hidden="true"
    />
  );
}
