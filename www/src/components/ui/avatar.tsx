"use client";

import * as AvatarPrimitive from "@radix-ui/react-avatar";
import { default as BoringAvatarComponent } from "boring-avatars";
import * as React from "react";

import { cn } from "@/lib/utils";

const BORING_AVATAR_COLORS = [
  "#FF0420",
  "#FFD700",
  "#87CEEB",
  "#7CFC00",
  "#FF7F50",
];

const Avatar = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Root>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Root
    ref={ref}
    className={cn(
      "relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full",
      className,
    )}
    {...props}
  />
));
Avatar.displayName = AvatarPrimitive.Root.displayName;

const AvatarImage = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Image>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Image>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Image
    ref={ref}
    className={cn("aspect-square h-full w-full", className)}
    {...props}
  />
));
AvatarImage.displayName = AvatarPrimitive.Image.displayName;

const AvatarFallback = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Fallback>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Fallback>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Fallback
    ref={ref}
    className={cn(
      "flex h-full w-full items-center justify-center rounded-full bg-muted",
      className,
    )}
    {...props}
  />
));
AvatarFallback.displayName = AvatarPrimitive.Fallback.displayName;

const BoringAvatar = ({ name }: { name: string }) => (
  <BoringAvatarComponent
    name={name}
    variant="beam"
    colors={BORING_AVATAR_COLORS}
  />
);

export { BoringAvatar, Avatar, AvatarImage, AvatarFallback };
