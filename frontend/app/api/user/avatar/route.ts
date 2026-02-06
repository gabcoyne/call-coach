/**
 * API route for uploading user avatar.
 *
 * POST /api/user/avatar - Upload user's profile picture
 *
 * Accepts: multipart/form-data with 'file' field
 * Returns: { success: true, url: string }
 */
import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";

export async function POST(request: NextRequest) {
  try {
    const { userId } = await auth();
    if (!userId) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      );
    }

    const formData = await request.formData();
    const file = formData.get("file") as File;

    if (!file) {
      return NextResponse.json(
        { error: "No file provided" },
        { status: 400 }
      );
    }

    // Validate file type
    const validTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];
    if (!validTypes.includes(file.type)) {
      return NextResponse.json(
        { error: "Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed" },
        { status: 400 }
      );
    }

    // Validate file size (max 5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      return NextResponse.json(
        { error: "File is too large. Maximum size is 5MB" },
        { status: 400 }
      );
    }

    // In production, you would:
    // 1. Upload to a cloud storage service (AWS S3, CloudFlare R2, etc.)
    // 2. Generate a URL for the uploaded file
    // 3. Save the URL in the database
    // 4. Return the URL

    // For now, return a mock URL
    const mockUrl = `https://example.com/avatars/${userId}/${Date.now()}-${file.name}`;

    console.log(`Avatar upload for user ${userId}: ${file.name} (${file.size} bytes)`);

    return NextResponse.json({
      success: true,
      url: mockUrl,
      fileName: file.name,
      fileSize: file.size,
    });
  } catch (error: any) {
    console.error("Failed to upload avatar:", error);
    return NextResponse.json(
      { error: "Failed to upload avatar", details: error.message },
      { status: 500 }
    );
  }
}
