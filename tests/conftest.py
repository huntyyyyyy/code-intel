"""Pytest plant: a tiny Spring-shaped Java tree plus a stub Gradle wrapper."""

from __future__ import annotations

from pathlib import Path

import pytest

from code_intel.settings import Settings

HOME = """package com.example;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class HomeController {
    @GetMapping("/")
    public String home() {
        return "ok";
    }
}
"""

CALLER = """package com.example;

public class TopicController {
    public void ping() {
        HomeController ignored = null;
    }
}
"""

SERVICE = """package com.example;

import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class TaxonomyMappingService {
    @Async
    @Transactional
    public void map() {}
}
"""

TEST = """package com.example;

import org.junit.jupiter.api.Test;

class HomeControllerTest {
    @Test
    void loads() {
        HomeController controller = null;
    }
}
"""

WRAPPER = """#!/bin/sh
echo "compileJava requested: $*"
if echo "$*" | grep -q failjava; then
  echo "e: src/main/java/com/example/Broken.java:4: error: boom"
  exit 1
fi
echo "BUILD SUCCESSFUL"
exit 0
"""


@pytest.fixture
def plant(tmp_path: Path) -> Path:
    java = tmp_path / "src" / "main" / "java" / "com" / "example"
    java.mkdir(parents=True)
    (java / "HomeController.java").write_text(HOME, encoding="utf-8")
    (java / "TopicController.java").write_text(CALLER, encoding="utf-8")
    (java / "TaxonomyMappingService.java").write_text(SERVICE, encoding="utf-8")
    tests = tmp_path / "src" / "test" / "java" / "com" / "example"
    tests.mkdir(parents=True)
    (tests / "HomeControllerTest.java").write_text(TEST, encoding="utf-8")
    (tmp_path / "build.gradle").write_text("plugins { id 'java' }\n", encoding="utf-8")
    wrapper = tmp_path / "gradlew"
    wrapper.write_text(WRAPPER, encoding="utf-8")
    wrapper.chmod(0o755)
    return tmp_path


@pytest.fixture
def settings(plant: Path) -> Settings:
    return Settings(plant_root=plant, java_home=None, serena_exe=None)
