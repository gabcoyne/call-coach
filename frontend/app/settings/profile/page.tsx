"use client";

import { useUser } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { User, Upload, Loader } from "lucide-react";

export default function ProfilePage() {
  const { user, isLoaded } = useUser();
  const router = useRouter();
  const [displayName, setDisplayName] = useState(user?.firstName || "");
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [avatarLoading, setAvatarLoading] = useState(false);
  const [savingName, setSavingName] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isLoaded) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <Loader className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="p-6">
        <Card>
          <CardContent className="p-6">
            <p className="text-muted-foreground">Please sign in to view your profile.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setAvatarLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/api/user/avatar", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Failed to upload avatar");

      // Update user profile picture URL in Clerk
      const data = await response.json();
      await user.setProfileImage({ file });

      setMessage({ type: "success", text: "Avatar updated successfully" });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error("Avatar upload failed:", error);
      setMessage({ type: "error", text: "Failed to upload avatar" });
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setAvatarLoading(false);
    }
  };

  const handleSaveDisplayName = async () => {
    if (!displayName.trim()) {
      setMessage({ type: "error", text: "Display name cannot be empty" });
      setTimeout(() => setMessage(null), 3000);
      return;
    }

    setSavingName(true);
    try {
      await user.update({
        firstName: displayName.trim(),
      });

      setMessage({ type: "success", text: "Display name updated successfully" });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error("Failed to update display name:", error);
      setMessage({ type: "error", text: "Failed to update display name" });
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setSavingName(false);
    }
  };

  const userEmail = user?.emailAddresses?.[0]?.emailAddress || "Not available";
  const userInitials =
    user?.firstName?.substring(0, 1).toUpperCase() ||
    user?.emailAddresses?.[0]?.emailAddress?.substring(0, 1).toUpperCase() ||
    "U";

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Profile Settings</h1>
        <p className="text-muted-foreground mt-1">
          Manage your account information and preferences
        </p>
      </div>

      {/* Status Message */}
      {message && (
        <div
          className={`p-4 rounded-lg ${
            message.type === "success"
              ? "bg-green-50 text-green-700 border border-green-200"
              : "bg-red-50 text-red-700 border border-red-200"
          }`}
        >
          {message.text}
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {/* Avatar Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Avatar
            </CardTitle>
            <CardDescription>Upload a profile picture</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col items-center gap-4">
              {user?.imageUrl ? (
                <img
                  src={user.imageUrl}
                  alt={displayName || "Profile"}
                  className="h-24 w-24 rounded-full object-cover border-2 border-border"
                />
              ) : (
                <div className="h-24 w-24 rounded-full bg-gradient-to-br from-prefect-pink to-prefect-sunrise1 flex items-center justify-center text-white text-2xl font-bold">
                  {userInitials}
                </div>
              )}
              <div className="flex gap-2 w-full">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarUpload}
                  className="hidden"
                />
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={avatarLoading}
                  className="flex-1"
                  variant="outline"
                >
                  {avatarLoading ? (
                    <>
                      <Loader className="h-4 w-4 mr-2 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Display Name Section */}
        <Card>
          <CardHeader>
            <CardTitle>Display Name</CardTitle>
            <CardDescription>How your name appears in the app</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="displayName">First Name</Label>
              <Input
                id="displayName"
                type="text"
                placeholder="Enter your display name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
              />
            </div>
            <Button
              onClick={handleSaveDisplayName}
              disabled={savingName || displayName === user?.firstName}
              className="w-full"
            >
              {savingName ? (
                <>
                  <Loader className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Email Section */}
      <Card>
        <CardHeader>
          <CardTitle>Email Address</CardTitle>
          <CardDescription>Your primary email account</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label className="text-muted-foreground">Primary Email</Label>
            <div className="p-3 bg-muted rounded-md text-foreground font-medium">{userEmail}</div>
          </div>
          <p className="text-sm text-muted-foreground">
            To change your email address, please manage your account in Clerk settings.
          </p>
        </CardContent>
      </Card>

      {/* Email Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>Email Preferences</CardTitle>
          <CardDescription>Control what emails you receive</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-3">
            <Checkbox
              id="emailNotifications"
              checked={emailNotifications}
              onCheckedChange={(checked) => setEmailNotifications(checked as boolean)}
            />
            <Label htmlFor="emailNotifications" className="font-normal cursor-pointer">
              Receive email notifications for important updates
            </Label>
          </div>
          <p className="text-sm text-muted-foreground">
            We'll send you emails about coaching insights, weekly reports, and system updates.
          </p>
        </CardContent>
      </Card>

      {/* Account Info */}
      <Card>
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
          <CardDescription>Your account details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-muted-foreground text-xs">User ID</Label>
              <p className="text-sm font-mono text-foreground truncate">{user?.id}</p>
            </div>
            <div>
              <Label className="text-muted-foreground text-xs">Account Status</Label>
              <p className="text-sm font-medium text-foreground">Active</p>
            </div>
          </div>
          <div>
            <Label className="text-muted-foreground text-xs">Member Since</Label>
            <p className="text-sm font-medium text-foreground">
              {user?.createdAt?.toLocaleDateString() || "Unknown"}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
