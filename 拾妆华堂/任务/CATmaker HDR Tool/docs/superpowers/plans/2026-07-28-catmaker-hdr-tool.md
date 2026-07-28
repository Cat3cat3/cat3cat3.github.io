# CATmaker HDR Tool MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and package a runnable macOS SwiftUI MVP that imports JPG, PNG, and HEIC images, previews a skin-aware luminance enhancement, and exports Gain Map HEIC when supported with explicit HEIC/JPEG fallback.

**Architecture:** A Swift Package executable keeps UI composition, editor state, image loading, pixel processing, and exporting in focused files. Pure tone and export-policy helpers are developed test-first; Core Image and ImageIO adapters implement the platform behavior behind those tested decisions. A shell script packages the release executable into a double-clickable `.app` without external dependencies.

**Tech Stack:** Swift 6, SwiftUI, AppKit, Core Image, ImageIO, Uniform Type Identifiers, XCTest, Swift Package Manager.

## Global Constraints

- Minimum deployment target: macOS 14 Sonoma.
- Project name and display name: `CATmaker HDR Tool`.
- Bundle identifier: `com.catmaker.hdrtool`.
- HDR intensity range: `0...2`, step `0.01`, default `1`.
- Accepted input: JPEG/JPG, PNG, HEIC/HEIF; one local image at a time.
- Export order: verified Gain Map HEIC on macOS 15+, visual-enhancement HEIC, then JPEG.
- No third-party dependencies, batch processing, ML face detection, App Store signing, notarization, or auto-update behavior.
- Do not modify, read into logs, or copy any bookkeeping, customer, price, order, or other project data.

---

## File Map

- `Package.swift`: Swift package manifest, executable product, test target, macOS 14 floor.
- `Sources/CATmakerHDRTool/App/CATmakerHDRToolApp.swift`: SwiftUI entry point and window sizing.
- `Sources/CATmakerHDRTool/Models/ImageDocument.swift`: loaded source URL, name, full-resolution CI image, and preview image.
- `Sources/CATmakerHDRTool/Models/ExportOutcome.swift`: export format, URL, Gain Map flag, and fallback message.
- `Sources/CATmakerHDRTool/Imaging/ToneMapping.swift`: pure, testable strength clamping and reference pixel math.
- `Sources/CATmakerHDRTool/Imaging/HDRProcessor.swift`: Core Image kernel, shared context, preview rendering, and SDR/HDR output pair.
- `Sources/CATmakerHDRTool/Imaging/ImageLoader.swift`: ImageIO type validation, orientation, and preview loading.
- `Sources/CATmakerHDRTool/Export/ExportPolicy.swift`: pure ordered attempt selection and human-readable fallback reasons.
- `Sources/CATmakerHDRTool/Export/ImageExporter.swift`: HEIF/JPEG encoding, Gain Map verification, temporary-file handling.
- `Sources/CATmakerHDRTool/Feature/EditorViewModel.swift`: import, debounced processing, export, and status state.
- `Sources/CATmakerHDRTool/Views/ContentView.swift`: minimal screen composition.
- `Sources/CATmakerHDRTool/Views/ImageDropZone.swift`: click and file-drop import surface.
- `Sources/CATmakerHDRTool/Views/ImagePreviewPane.swift`: titled aspect-fit image preview.
- `Tests/CATmakerHDRToolTests/ToneMappingTests.swift`: reference curve and skin-protection tests.
- `Tests/CATmakerHDRToolTests/ImageLoaderTests.swift`: generated fixture acceptance and invalid-data tests.
- `Tests/CATmakerHDRToolTests/ExportPolicyTests.swift`: export ordering and reason tests.
- `Tests/CATmakerHDRToolTests/ImageExporterTests.swift`: real encoder, extension, and post-write inspection tests.
- `scripts/build-app.sh`: release build and deterministic `.app` assembly.
- `scripts/smoke-test-app.sh`: launch/keep-alive/terminate check.
- `README.md`: run, package, capability, and fallback instructions.

### Task 1: Package Skeleton and Tone-Mapping Contract

**Files:**
- Create: `Package.swift`
- Create: `Sources/CATmakerHDRTool/Imaging/ToneMapping.swift`
- Create: `Tests/CATmakerHDRToolTests/ToneMappingTests.swift`

**Interfaces:**
- Produces: `HDRSettings.defaultIntensity`, `HDRSettings.clamped(_:)`, `RGB`, `ToneMapping.evaluate(_:intensity:)`, and `ToneMapping.skinProtection(for:)`.
- Consumes: no project interfaces.

- [ ] **Step 1: Create the package manifest and write failing tone tests**

Use a macOS 14 executable and XCTest target:

```swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "CATmakerHDRTool",
    platforms: [.macOS(.v14)],
    products: [.executable(name: "CATmakerHDRTool", targets: ["CATmakerHDRTool"])],
    targets: [
        .executableTarget(name: "CATmakerHDRTool"),
        .testTarget(name: "CATmakerHDRToolTests", dependencies: ["CATmakerHDRTool"])
    ],
    swiftLanguageModes: [.v5]
)
```

Write tests that name the production change they protect and assert real values:

```swift
import XCTest
@testable import CATmakerHDRTool

final class ToneMappingTests: XCTestCase {
    func testDefaultAndClampedIntensityStayInsideEditorRange() {
        XCTAssertEqual(HDRSettings.defaultIntensity, 1)
        XCTAssertEqual(HDRSettings.clamped(-0.5), 0)
        XCTAssertEqual(HDRSettings.clamped(2.5), 2)
    }

    func testZeroIntensityPreservesEveryChannel() {
        let input = RGB(r: 0.23, g: 0.48, b: 0.82)
        XCTAssertEqual(ToneMapping.evaluate(input, intensity: 0), input)
    }

    func testShadowsLiftLessThanHighlightsAndSDRStaysBelowOne() {
        let shadow = ToneMapping.evaluate(.gray(0.08), intensity: 1)
        let midtone = ToneMapping.evaluate(.gray(0.50), intensity: 1)
        let highlight = ToneMapping.evaluate(.gray(0.82), intensity: 1)
        XCTAssertGreaterThan(shadow.r, 0.08)
        XCTAssertLessThan(shadow.r - 0.08, 0.06)
        XCTAssertLessThan(abs(midtone.r - 0.50), 0.08)
        XCTAssertGreaterThan(highlight.r, 0.82)
        XCTAssertLessThan(highlight.r, 1.0)
    }

    func testBrightSkinReceivesLessGainThanEquallyBrightBlue() {
        let skin = RGB(r: 0.88, g: 0.66, b: 0.52)
        let blue = RGB(r: 0.52, g: 0.70, b: 0.88)
        let skinGain = ToneMapping.evaluate(skin, intensity: 2).luminance - skin.luminance
        let blueGain = ToneMapping.evaluate(blue, intensity: 2).luminance - blue.luminance
        XCTAssertGreaterThan(ToneMapping.skinProtection(for: skin), 0.35)
        XCTAssertGreaterThan(blueGain, skinGain)
    }
}
```

- [ ] **Step 2: Run tests and verify RED**

Run: `swift test --filter ToneMappingTests`

Expected: compilation fails because `HDRSettings`, `RGB`, and `ToneMapping` do not exist.

- [ ] **Step 3: Implement the smallest pure reference model**

Create `Sendable` value types. Use Rec. 709 luminance, smoothstep masks, a small decaying shadow lift, a highlight lift, skin-weight attenuation, and `x / (1 + max(0, x - knee))`-style soft compression. Special-case intensity zero to return the exact input value. Keep each channel in `0..<1` for the SDR reference result.

Required signatures:

```swift
enum HDRSettings {
    static let defaultIntensity = 1.0
    static func clamped(_ value: Double) -> Double
}

struct RGB: Equatable, Sendable {
    var r: Double
    var g: Double
    var b: Double
    static func gray(_ value: Double) -> RGB
    var luminance: Double { get }
}

enum ToneMapping {
    static func skinProtection(for rgb: RGB) -> Double
    static func evaluate(_ input: RGB, intensity: Double) -> RGB
}
```

- [ ] **Step 4: Run tests and verify GREEN**

Run: `swift test --filter ToneMappingTests`

Expected: four tests pass with zero failures.

- [ ] **Step 5: Commit the independently tested tone contract**

```bash
git add Package.swift Sources/CATmakerHDRTool/Imaging/ToneMapping.swift Tests/CATmakerHDRToolTests/ToneMappingTests.swift
git commit -m "feat: define HDR tone mapping contract"
```

### Task 2: ImageIO Loading and Core Image Processing

**Files:**
- Create: `Sources/CATmakerHDRTool/Models/ImageDocument.swift`
- Create: `Sources/CATmakerHDRTool/Imaging/ImageLoader.swift`
- Create: `Sources/CATmakerHDRTool/Imaging/HDRProcessor.swift`
- Create: `Tests/CATmakerHDRToolTests/ImageLoaderTests.swift`
- Modify: `Tests/CATmakerHDRToolTests/ToneMappingTests.swift`

**Interfaces:**
- Consumes: `HDRSettings.clamped(_:)` and tone constants established by Task 1.
- Produces: `ImageDocument`, `ImageLoader.load(from:)`, `HDRProcessor.process(_:intensity:)`, `HDRProcessor.makePreview(_:maxPixelSize:)`, and `ProcessedImages`.

- [ ] **Step 1: Write failing generated-fixture loader tests**

Create 8 × 8 red `CGImage` fixtures in the test file and encode them with `CGImageDestination` to `UTType.jpeg`, `UTType.png`, and, only when present in `CGImageDestinationCopyTypeIdentifiers()`, `UTType.heic`. Test:

```swift
func testLoaderAcceptsGeneratedJPEGAndPNG() throws {
    for type in [UTType.jpeg, .png] {
        let url = try FixtureImage.write(type: type)
        let document = try ImageLoader().load(from: url)
        XCTAssertEqual(document.sourceURL, url)
        XCTAssertEqual(document.image.extent.size, CGSize(width: 8, height: 8))
    }
}

func testLoaderAcceptsHEICWhenTheInstalledEncoderSupportsIt() throws {
    try XCTSkipUnless(FixtureImage.canEncode(.heic))
    let url = try FixtureImage.write(type: .heic)
    XCTAssertNoThrow(try ImageLoader().load(from: url))
}

func testLoaderRejectsTextRenamedToJPG() throws {
    let url = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".jpg")
    try Data("not an image".utf8).write(to: url)
    XCTAssertThrowsError(try ImageLoader().load(from: url))
}
```

- [ ] **Step 2: Run loader tests and verify RED**

Run: `swift test --filter ImageLoaderTests`

Expected: compilation fails because `ImageLoader` and `ImageDocument` do not exist.

- [ ] **Step 3: Implement ImageIO validation and orientation**

Define:

```swift
struct ImageDocument: @unchecked Sendable {
    let sourceURL: URL
    let displayName: String
    let image: CIImage
    let originalPreview: CGImage
}

enum ImageLoadingError: LocalizedError {
    case inaccessible, invalidImage, unsupportedType(String), renderFailed
}

struct ImageLoader {
    func load(from url: URL) throws -> ImageDocument
}
```

`load(from:)` must create a `CGImageSource`, accept only `public.jpeg`, `public.png`, `public.heic`, or `public.heif` conformance, read index 0 with caching disabled, initialize `CIImage` with `.applyOrientationProperty: true`, translate the finite extent to origin, and create an aspect-preserving preview with a maximum dimension of 1800 pixels.

- [ ] **Step 4: Run loader tests and verify GREEN**

Run: `swift test --filter ImageLoaderTests`

Expected: JPEG, PNG, and invalid-data tests pass; HEIC passes or is reported as skipped only when the installed encoder is unavailable.

- [ ] **Step 5: Add a failing Core Image/reference parity test**

For several 1 × 1 colors, render `HDRProcessor.process(...).displayImage` into RGBA float pixels and compare each channel to `ToneMapping.evaluate` with tolerance `0.015`. Also assert `extendedImage` has a value above 1.0 for a bright non-skin input at intensity 2 and stays finite.

- [ ] **Step 6: Run the processor test and verify RED**

Run: `swift test --filter ToneMappingTests/testCoreImageKernelMatchesReferenceSamples`

Expected: compilation fails because `HDRProcessor` and `ProcessedImages` do not exist.

- [ ] **Step 7: Implement the shared Core Image processor**

Define:

```swift
struct ProcessedImages: @unchecked Sendable {
    let displayImage: CIImage
    let extendedImage: CIImage
}

final class HDRProcessor: @unchecked Sendable {
    static let shared = HDRProcessor()
    let context: CIContext
    func process(_ image: CIImage, intensity: Double) throws -> ProcessedImages
    func makePreview(_ image: CIImage, maxPixelSize: CGFloat) throws -> CGImage
}
```

The `CIColorKernel` must mirror the pure reference formulas. Return exact input images for zero intensity. The SDR output uses soft compression below 1.0; the extended output keeps bounded values up to a content headroom derived from intensity. Crop both outputs to the input extent.

- [ ] **Step 8: Run all Task 2 tests**

Run: `swift test --filter 'ImageLoaderTests|ToneMappingTests'`

Expected: all tests pass, with only capability-based HEIC skip allowed.

- [ ] **Step 9: Commit loading and processing**

```bash
git add Sources/CATmakerHDRTool/Models Sources/CATmakerHDRTool/Imaging Tests/CATmakerHDRToolTests
git commit -m "feat: load and enhance supported images"
```

### Task 3: Export Policy, HEIC Gain Map, and JPEG Fallback

**Files:**
- Create: `Sources/CATmakerHDRTool/Models/ExportOutcome.swift`
- Create: `Sources/CATmakerHDRTool/Export/ExportPolicy.swift`
- Create: `Sources/CATmakerHDRTool/Export/ImageExporter.swift`
- Create: `Tests/CATmakerHDRToolTests/ExportPolicyTests.swift`
- Create: `Tests/CATmakerHDRToolTests/ImageExporterTests.swift`

**Interfaces:**
- Consumes: `ProcessedImages` and shared `CIContext` from Task 2.
- Produces: `ExportAttempt`, `ExportPolicy.attempts(for:)`, `ExportOutcome`, and `ImageExporter.export(_:preferredURL:)`.

- [ ] **Step 1: Write failing export-policy tests**

```swift
final class ExportPolicyTests: XCTestCase {
    func testGainMapCapableSystemTriesAllFormatsInRequiredOrder() {
        XCTAssertEqual(
            ExportPolicy.attempts(for: .init(canWriteHEIC: true, canWriteGainMap: true)),
            [.gainMapHEIC, .visualHEIC, .jpeg]
        )
    }

    func testSystemWithoutGainMapStillPrefersVisualHEIC() {
        XCTAssertEqual(
            ExportPolicy.attempts(for: .init(canWriteHEIC: true, canWriteGainMap: false)),
            [.visualHEIC, .jpeg]
        )
    }

    func testSystemWithoutHEICUsesJPEG() {
        XCTAssertEqual(
            ExportPolicy.attempts(for: .init(canWriteHEIC: false, canWriteGainMap: false)),
            [.jpeg]
        )
    }
}
```

- [ ] **Step 2: Run policy tests and verify RED**

Run: `swift test --filter ExportPolicyTests`

Expected: compilation fails because export policy types do not exist.

- [ ] **Step 3: Implement the pure policy and result models**

Required signatures:

```swift
enum ExportAttempt: Equatable, Sendable { case gainMapHEIC, visualHEIC, jpeg }

struct ExportCapabilities: Equatable, Sendable {
    let canWriteHEIC: Bool
    let canWriteGainMap: Bool
}

enum ExportFormat: String, Sendable { case heic, jpeg }

struct ExportOutcome: Sendable {
    let url: URL
    let format: ExportFormat
    let containsGainMap: Bool
    let message: String
}

enum ExportPolicy {
    static func attempts(for capabilities: ExportCapabilities) -> [ExportAttempt]
}
```

- [ ] **Step 4: Run policy tests and verify GREEN**

Run: `swift test --filter ExportPolicyTests`

Expected: three tests pass.

- [ ] **Step 5: Write failing real-encoder tests**

Construct a finite 16 × 16 `ProcessedImages` pair, export to a temporary URL, open the output with `CGImageSource`, and assert:

```swift
func testExportProducesAnInspectableFileWithMatchingExtension() throws {
    let outcome = try ImageExporter().export(fixtures, preferredURL: temporary.appendingPathComponent("result.heic"))
    XCTAssertTrue(FileManager.default.fileExists(atPath: outcome.url.path))
    XCTAssertNotNil(CGImageSourceCreateWithURL(outcome.url as CFURL, nil))
    XCTAssertEqual(outcome.url.pathExtension.lowercased(), outcome.format == .heic ? "heic" : "jpg")
}

func testReportedGainMapIsPresentInWrittenFile() throws {
    let outcome = try ImageExporter().export(fixtures, preferredURL: temporary.appendingPathComponent("gain.heic"))
    if outcome.containsGainMap {
        XCTAssertTrue(ImageExporter.fileContainsGainMap(at: outcome.url))
    }
}
```

- [ ] **Step 6: Run exporter tests and verify RED**

Run: `swift test --filter ImageExporterTests`

Expected: compilation fails because `ImageExporter` does not exist.

- [ ] **Step 7: Implement safe encoding and verification**

Define:

```swift
struct ImageExporter: Sendable {
    func capabilities() -> ExportCapabilities
    func export(_ images: ProcessedImages, preferredURL: URL) throws -> ExportOutcome
    static func fileContainsGainMap(at url: URL) -> Bool
}
```

Implementation requirements:

- Detect HEIC support from `CGImageDestinationCopyTypeIdentifiers()`.
- Set `canWriteGainMap` only on macOS 15+ when HEIC is available.
- For `.gainMapHEIC`, call Core Image HEIF representation with the SDR image as receiver and `.hdrImage: extendedImage`; write to a sibling temporary URL, then verify `kCGImageAuxiliaryDataTypeHDRGainMap` or `kCGImageAuxiliaryDataTypeISOGainMap` with ImageIO.
- For `.visualHEIC`, render `displayImage` using extended-linear sRGB input and Display P3 or sRGB output with quality `0.92`.
- For `.jpeg`, render an opaque sRGB image with quality `0.94` and a `.jpg` extension.
- Remove only the exporter-created temporary file. Atomically replace the chosen final URL only after encoding and inspection succeed.
- Accumulate failed-attempt reasons in the successful `message`; throw a localized error containing all reasons only if every attempt fails.

- [ ] **Step 8: Run exporter and full tests**

Run: `swift test`

Expected: all tests pass; Gain Map assertions run only when the returned outcome claims a map.

- [ ] **Step 9: Commit the export pipeline**

```bash
git add Sources/CATmakerHDRTool/Export Sources/CATmakerHDRTool/Models/ExportOutcome.swift Tests/CATmakerHDRToolTests
git commit -m "feat: export HDR HEIC with explicit fallback"
```

### Task 4: SwiftUI Editor and Drag-and-Drop Workflow

**Files:**
- Create: `Sources/CATmakerHDRTool/App/CATmakerHDRToolApp.swift`
- Create: `Sources/CATmakerHDRTool/Feature/EditorViewModel.swift`
- Create: `Sources/CATmakerHDRTool/Views/ContentView.swift`
- Create: `Sources/CATmakerHDRTool/Views/ImageDropZone.swift`
- Create: `Sources/CATmakerHDRTool/Views/ImagePreviewPane.swift`
- Create: `Tests/CATmakerHDRToolTests/EditorViewModelTests.swift`

**Interfaces:**
- Consumes: `ImageLoader`, `HDRProcessor`, `ImageExporter`, `ImageDocument`, and `ExportOutcome`.
- Produces: runnable SwiftUI `@main` application and editor actions `importImage(from:)`, `schedulePreview()`, and `export(to:)`.

- [ ] **Step 1: Write failing editor-state tests with protocol-backed real fakes**

Introduce narrow protocols (`ImageLoading`, `ImageProcessing`, `ImageExporting`) whose methods match the production services. Test that initial intensity is 1, a successful import sets both previews and a success status, failed import retains the previous document, and a stale preview generation cannot replace a newer generation.

Example state assertion:

```swift
@MainActor
func testInitialStateUsesRequiredDefaultIntensity() {
    let model = EditorViewModel(loader: StubLoader(), processor: StubProcessor(), exporter: StubExporter())
    XCTAssertEqual(model.intensity, 1)
    XCTAssertNil(model.document)
    XCTAssertFalse(model.canExport)
}
```

- [ ] **Step 2: Run view-model tests and verify RED**

Run: `swift test --filter EditorViewModelTests`

Expected: compilation fails because `EditorViewModel` and its service protocols do not exist.

- [ ] **Step 3: Implement observable editor coordination**

`EditorViewModel` is `@MainActor final class` using `ObservableObject`. It publishes `document`, `processedPreview`, `intensity`, `isBusy`, and `statusText`. Changing `intensity` clamps the value and schedules a 120 ms debounced task. Each request increments a generation counter; only the latest generation may publish a result. Import errors retain current state. Export maps `ExportOutcome.message` directly to the status line.

- [ ] **Step 4: Run view-model tests and verify GREEN**

Run: `swift test --filter EditorViewModelTests`

Expected: all editor-state tests pass.

- [ ] **Step 5: Build the minimal SwiftUI screen**

Implement:

- An `ImageDropZone` accepting one `.fileURL` provider, decoding the URL on the main actor, and calling `onImport`.
- A click action using `NSOpenPanel` filtered to `.jpeg`, `.png`, `.heic`, and `.heif`.
- Two `ImagePreviewPane` views in an `HStack`, titled “原图” and “处理后”, with aspect-fit rendering.
- A `Slider(value:in:step:)` bound to `0...2` and `0.01`.
- An export `NSSavePanel` defaulting to `<source>-CATmaker-HDR.heic`.
- A one-line status label with an icon and accessible labels on import, slider, and export controls.
- A window default size of 980 × 700 and minimum size of 760 × 560.

- [ ] **Step 6: Compile and re-run the complete tests**

Run: `swift build && swift test`

Expected: debug build and all tests succeed with no Swift compiler errors.

- [ ] **Step 7: Commit the runnable UI workflow**

```bash
git add Sources/CATmakerHDRTool/App Sources/CATmakerHDRTool/Feature Sources/CATmakerHDRTool/Views Tests/CATmakerHDRToolTests/EditorViewModelTests.swift
git commit -m "feat: add minimal SwiftUI HDR editor"
```

### Task 5: App Bundle Packaging, Documentation, and End-to-End Verification

**Files:**
- Create: `scripts/build-app.sh`
- Create: `scripts/smoke-test-app.sh`
- Create: `README.md`
- Create: `Tests/CATmakerHDRToolTests/RequirementCoverageTests.swift`
- Modify: files found by verification only when a requirement is disproven.

**Interfaces:**
- Consumes: the `CATmakerHDRTool` release executable.
- Produces: `dist/CATmaker HDR Tool.app` and documented run/package commands.

- [ ] **Step 1: Write a failing bundle-structure requirement test**

The test runs only when `CATMAKER_APP_PATH` is present. It reads `Contents/Info.plist` and asserts:

```swift
XCTAssertEqual(plist["CFBundleDisplayName"] as? String, "CATmaker HDR Tool")
XCTAssertEqual(plist["CFBundleIdentifier"] as? String, "com.catmaker.hdrtool")
XCTAssertEqual(plist["LSMinimumSystemVersion"] as? String, "14.0")
XCTAssertTrue(FileManager.default.isExecutableFile(atPath: appending("Contents/MacOS/CATmakerHDRTool")))
```

- [ ] **Step 2: Run the requirement test and verify RED**

Run: `CATMAKER_APP_PATH="$PWD/dist/CATmaker HDR Tool.app" swift test --filter RequirementCoverageTests`

Expected: failure because the `.app` bundle does not exist.

- [ ] **Step 3: Implement deterministic app packaging**

`scripts/build-app.sh` must:

1. Resolve its own project directory without using `$HOME`.
2. Run `swift build -c release`.
3. Create `dist/CATmaker HDR Tool.app/Contents/{MacOS,Resources}`.
4. Copy `.build/release/CATmakerHDRTool` into `Contents/MacOS`.
5. Write `Info.plist` containing the required display name, bundle ID, executable, `APPL` package type, `14.0` minimum version, high-resolution capability, and copyright-free metadata.
6. Run `plutil -lint` and `codesign --force --deep --sign -` when `codesign` is available; ad-hoc signing failure must stop the script.

- [ ] **Step 4: Package and verify GREEN**

Run:

```bash
./scripts/build-app.sh
CATMAKER_APP_PATH="$PWD/dist/CATmaker HDR Tool.app" swift test --filter RequirementCoverageTests
```

Expected: package succeeds and bundle requirement tests pass.

- [ ] **Step 5: Add a bounded process smoke test**

`scripts/smoke-test-app.sh` must launch the bundle executable directly, poll for up to 5 seconds without a blocking sleep longer than 1 second, fail if the process exits early, send `TERM`, wait for exit, and report success. It must write any process log only below `.build/smoke/`.

- [ ] **Step 6: Document the MVP and its honest capability boundary**

`README.md` must include:

- `swift run` for development.
- `./scripts/build-app.sh` and the exact `.app` location.
- Drag/drop and click import instructions.
- Intensity semantics: 0 original, 1 default, 2 maximum protected enhancement.
- macOS 15+ Gain Map attempt and write-back verification.
- macOS 14/encoder failure HEIC/JPEG fallback and status-message behavior.
- The absence of signing/notarization for distribution.

- [ ] **Step 7: Run fresh full verification**

Run sequentially and inspect complete output:

```bash
swift test
swift build -c release
./scripts/build-app.sh
CATMAKER_APP_PATH="$PWD/dist/CATmaker HDR Tool.app" swift test --filter RequirementCoverageTests
./scripts/smoke-test-app.sh
```

Expected: zero test failures, successful release build, valid app bundle, passing requirements, and a process that stays alive until terminated by the smoke test.

- [ ] **Step 8: Perform the requirement-by-requirement audit**

Inspect source and fresh evidence for: supported input types; dual preview; intensity range/default; luminance-based highlight, midtone, shadow, and skin behavior; HEIC preference; Gain Map attempt and post-write verification; JPEG fallback; visible fallback reason; minimal UI; comments on non-obvious image and export code; runnable app bundle. Record any gap as a failing test or build check and fix it before completion.

- [ ] **Step 9: Commit packaging and documentation**

```bash
git add scripts README.md Tests/CATmakerHDRToolTests/RequirementCoverageTests.swift
git commit -m "build: package and verify CATmaker HDR Tool"
```
